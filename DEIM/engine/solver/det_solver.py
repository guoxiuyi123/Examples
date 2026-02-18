"""
DEIM: DETR with Improved Matching for Fast Convergence
Copyright (c) 2024 The DEIM Authors. All Rights Reserved. 
---------------------------------------------------------------------------------
Modified from D-FINE (https://github.com/Peterande/D-FINE)   
Copyright (c) 2024 D-FINE authors. All Rights Reserved.
"""
   
import time
import json    
import datetime
import copy
import gc

import torch

from ..misc import dist_utils, stats, get_weight_size   

from ._solver import BaseSolver, ModelSaverFunc    
from .det_engine import train_one_epoch, distill_one_epoch, evaluate    
from ..optim.lr_scheduler import FlatCosineLRScheduler  
from ..logger_module import get_logger     
from ..extre_module.torch_utils import FeatureExtractor
from ..extre_module.distill_utils import FeatureLoss, DETRLogicLoss, DETRMutilDecoderLogicLoss

RED, GREEN, BLUE, YELLOW, ORANGE, RESET = "\033[91m", "\033[92m", "\033[94m", "\033[93m", "\033[38;5;208m", "\033[0m"  
logger = get_logger(__name__)
coco_name_list = ['ap', 'ap50', 'ap75', 'aps', 'apm', 'apl', 'ar', 'ar50', 'ar75', 'ars', 'arm', 'arl']  
coco_name_tiny_list = ['ap', 'ap50', 'ap75', 'apt', 'aps', 'apm', 'apl', 'ar', 'ar50', 'ar75', 'art', 'ars', 'arm', 'arl'] 

class DetSolver(BaseSolver):     
     
    def fit(self, cfg_str):
        self.train()
        args = self.cfg  

        if dist_utils.is_main_process():
            with open(self.output_dir / 'args.json', 'w') as json_file:
                json_file.write(cfg_str)

        # 计算模型参数量、FLOPs 等统计信息 
        n_parameters, model_stats = stats(self.cfg)
        print(model_stats)
        # print("-"*42 + "Start training" + "-"*43)
        logger.info("Start training")  
   
        # 初始化学习率调度器   
        self.self_lr_scheduler = False
        if args.lrsheduler is not None:
            iter_per_epoch = len(self.train_dataloader)    
            # print("     ## Using Self-defined Scheduler-{} ## ".format(args.lrsheduler))
            logger.info("     ## Using Self-defined Scheduler-{} ## ".format(args.lrsheduler)) 
            self.lr_scheduler = FlatCosineLRScheduler(self.optimizer, args.lr_gamma, iter_per_epoch, total_epochs=args.epoches,     
                                                warmup_iter=args.warmup_iter, flat_epochs=args.flat_epoch, no_aug_epochs=args.no_aug_epoch, lr_scyedule_save_path=self.output_dir)   
            self.self_lr_scheduler = True
        # 统计需要训练的参数数量
        n_parameters = sum([p.numel() for p in self.model.parameters() if p.requires_grad])
        # print(f'number of trainable parameters: {n_parameters}')
        logger.info(f'number of trainable parameters: {n_parameters}')   
   
        self.criterion.set_model(self.model)
        best_stat = {'epoch': -1, }
        # evaluate again before resume training
        if self.last_epoch > 0:
            module = self.ema.module if self.ema else self.model
            test_stats, coco_evaluator = evaluate(  
                module, 
                self.criterion, 
                self.postprocessor,  
                self.val_dataloader,     
                self.evaluator,  
                self.device,     
                yolo_metrice=self.cfg.yolo_metrice
            )   
            if test_stats:    
                # 收集所有指标并计算平均值
                metrics = {k: test_stats[k][0] for k in test_stats}
                avg_metric = sum(metrics.values()) / len(metrics)   
     
                # 初始化best_stat
                best_stat['epoch'] = self.last_epoch
                best_stat['avg_metric'] = avg_metric
                best_stat.update(metrics)    
 
                logger.info(f'Resume from epoch {self.last_epoch}:')   
                logger.info(f'  Avg metric: {avg_metric:.4f}')  
                for k, v in metrics.items():
                    logger.info(f'  {k}: {v:.4f}')
                logger.info(f'best_stat: {best_stat}')

        start_time = time.time()
        start_epoch = self.last_epoch + 1    
        for epoch in range(start_epoch, args.epoches):
   
            self.train_dataloader.set_epoch(epoch)
            self.criterion.set_epoch(epoch)
            # self.train_dataloader.dataset.set_epoch(epoch)    
            if dist_utils.is_dist_available_and_initialized():
                self.train_dataloader.sampler.set_epoch(epoch)

            if epoch == self.train_dataloader.collate_fn.stop_epoch:     
                self.load_resume_state(str(self.output_dir / 'best_stg1.pth'))
                self.ema.decay = self.train_dataloader.collate_fn.ema_restart_decay   
                # print(f'Refresh EMA at epoch {epoch} with decay {self.ema.decay}')    
                logger.info(f'Refresh EMA at epoch {epoch} with decay {self.ema.decay}')
     
            # 训练一个 epoch    
            train_stats = train_one_epoch(    
                self.self_lr_scheduler,  
                self.lr_scheduler,
                self.model, 
                self.criterion, 
                self.train_dataloader,    
                self.optimizer,     
                self.device,     
                epoch, 
                max_norm=args.clip_max_norm, 
                print_freq=args.print_freq,    
                ema=self.ema, 
                scaler=self.scaler, 
                lr_warmup_scheduler=self.lr_warmup_scheduler,    
                writer=self.writer,     
                plot_train_batch_freq=args.plot_train_batch_freq,     
                output_dir=self.output_dir,   
                epoches=args.epoches, # 总的训练次数     
                verbose_type=args.verbose_type
            )   

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()
  
            if not self.self_lr_scheduler:  # update by epoch 
                if self.lr_warmup_scheduler is None or self.lr_warmup_scheduler.finished():
                    self.lr_scheduler.step()

            self.last_epoch += 1

            if self.output_dir and epoch < self.train_dataloader.collate_fn.stop_epoch:
                checkpoint_paths = [self.output_dir / 'last.pth']
                # extra checkpoint before LR drop and every 100 epochs     
                if (epoch + 1) % args.checkpoint_freq == 0:
                    checkpoint_paths.append(self.output_dir / f'checkpoint{epoch:04}.pth')   
                with ModelSaverFunc(self):
                    for checkpoint_path in checkpoint_paths: 
                        dist_utils.save_on_master(self.state_dict(), checkpoint_path)

            # 训练一个epoch后计算模型指标     
            module = self.ema.module if self.ema else self.model
            test_stats, coco_evaluator = evaluate(
                module,
                self.criterion,   
                self.postprocessor, 
                self.val_dataloader,   
                self.evaluator,
                self.device,
                yolo_metrice=self.cfg.yolo_metrice    
            ) 

            if torch.cuda.is_available():
                torch.cuda.empty_cache()     
                gc.collect()     
            
            best_stat = self.save_best_model(test_stats, best_stat, epoch)  

            log_stats = {
                **{f'train_{k}': v for k, v in train_stats.items()},  
                **{f'test_{k}': v for k, v in test_stats.items()},
                'epoch': epoch,  
                'n_parameters': n_parameters   
            }   

            if self.output_dir and dist_utils.is_main_process():
                with (self.output_dir / "log.txt").open("a") as f:
                    f.write(json.dumps(log_stats) + "\n")    

                # for evaluation logs   
                # if coco_evaluator is not None:   
                #     (self.output_dir / 'eval').mkdir(exist_ok=True)
                #     if "bbox" in coco_evaluator.coco_eval:
                #         filenames = ['latest.pth']   
                #         if epoch % 50 == 0:     
                #             filenames.append(f'{epoch:03}.pth')
                #         for name in filenames:   
                #             torch.save(coco_evaluator.coco_eval["bbox"].eval,
                #                     self.output_dir / "eval" / name)

        total_time = time.time() - start_time    
        total_time_str = str(datetime.timedelta(seconds=int(total_time)))     
        logger.info('Training time {}'.format(total_time_str))


    def val(self, ):
        self.eval()     
  
        module = self.ema.module if self.ema else self.model
        module.deploy()
        _, model_info = stats(self.cfg, module=module)
        logger.info(GREEN + f"Model Info(fused) {model_info}" + RESET)
        get_weight_size(module)
        test_stats, coco_evaluator = evaluate(module, self.criterion, self.postprocessor,
                self.val_dataloader, self.evaluator, self.device, True, self.output_dir, self.cfg.yolo_metrice)     
  
        if self.output_dir:    
            dist_utils.save_on_master(coco_evaluator.coco_eval["bbox"].eval, self.output_dir / "eval.pth")
  
        return
    
    def val_onnx_engine(self, mode):    
        
        self.cfg.yaml_cfg['val_dataloader']['total_batch_size'] = 1
        self.cfg.yaml_cfg['eval_mask_ratio'] = 1    

        self.eval()    
        logger.warning(RED + f"仅支持batch_size=1进行验证" + RESET)
        if self.cfg.path.endswith('onnx'):     
            import onnxruntime as ort     
            model = ort.InferenceSession(self.cfg.path)   
            logger.info(f"Loading Onnx Model: {self.cfg.path}")
            logger.info(f"Using device: {ort.get_device()}") 
            model = {'onnx':model} 
        elif self.cfg.path.endswith('engine'):     
            if mode == 'det':
                from tools.inference.detect.trt_inf import TRTInference  
            elif mode == 'mask':
                from tools.inference.segment.trt_inf import TRTInference
            model = TRTInference(self.cfg.path, device=self.device)
            logger.info(f"Loading Onnx Model: {self.cfg.path}")
            logger.info(f"Using device: {self.device}")
            model = {'engine':model}
  
        test_stats, coco_evaluator = evaluate(None, self.criterion, self.postprocessor,
                self.val_dataloader, self.evaluator, self.device, True, self.output_dir, self.cfg.yolo_metrice, model)
   
        if self.output_dir: 
            dist_utils.save_on_master(coco_evaluator.coco_eval["bbox"].eval, self.output_dir / "eval.pth")
 
        return

    def distill(self, student_cfg_str, teacher_cfg_str, teacher_cfg):
        self.train() 
        args = self.cfg

        if dist_utils.is_main_process():
            with open(self.output_dir / 'student_args.json', 'w') as json_file:    
                json_file.write(student_cfg_str)
 
            with open(self.output_dir / 'teacher_args.json', 'w') as json_file:     
                json_file.write(teacher_cfg_str)
 
        # 计算 kd_loss_epoch 
        if self.cfg.kd_loss_epoch < 0.0 or self.cfg.kd_loss_epoch > 1.0:
            logger.info(RED + f'kd_loss_epoch should be set within the range of 0 to 1, Now set {self.cfg.kd_loss_epoch}, reset 1.0' + RESET)  
            self.cfg.kd_loss_epoch = 1.0 
        distill_epoch = int(self.cfg.kd_loss_epoch * args.epoches)
        if self.cfg.kd_loss_epoch == 1.0:
            logger.info(RED + f'kd_loss_epoch set {self.cfg.kd_loss_epoch}, Distillation learning is used throughout the entire training process.' + RESET)  
        else:
            logger.info(RED + f'kd_loss_epoch set {self.cfg.kd_loss_epoch}, For the first {distill_epoch} epochs, use distillation for learning, and for the last {args.epoches - distill_epoch} epochs, train normally.' + RESET)

        # 计算模型参数量、FLOPs 等统计信息 student     
        logger.info(RED + '----------- student -----------' + RESET)
        n_parameters, model_stats = stats(self.cfg) 
        print(model_stats)   
  
        # 计算模型参数量、FLOPs 等统计信息 teacher
        logger.info(RED + '----------- teacher -----------' + RESET)
        n_parameters, model_stats = stats(teacher_cfg) 
        print(model_stats)

        student_is_Ultralytics = self.cfg.yaml_cfg['model'] == 'DEIM_MG'   
        teacher_is_Ultralytics = teacher_cfg.yaml_cfg['model'] == 'DEIM_MG'
        logger.info(RED + f'student_is_Ultralytics:{student_is_Ultralytics} teacher_is_Ultralytics:{teacher_is_Ultralytics}' + RESET)
  
        # teacher model init
        self.teacher_model = teacher_cfg.model     

        # NOTE: Must load_tuning_state before EMA instance building  
        if teacher_cfg.tuning:
            logger.info(RED + f'Teahcer | Loading checkpoint from {teacher_cfg.tuning}' + RESET)
            checkpoint = torch.load(teacher_cfg.tuning, map_location='cpu')     
            if 'ema' in checkpoint:     
                state = checkpoint['ema']['module'] 
            else:     
                state = checkpoint['model']    
            try: 
                self.teacher_model.load_state_dict(state)
                logger.info(RED + f'Teahcer | Load checkpoint from {teacher_cfg.tuning} Success.✅' + RESET)
            except Exception as e:     
                logger.error(f"{e} \n 教师模型所选择的配置文件对应的网络结构与指定的教师权重不一致，请检查或者重新训练。❌")
                exit(0)

        self.teacher_model = dist_utils.warp_model(
            self.teacher_model.to(self.device), sync_bn=teacher_cfg.sync_bn, find_unused_parameters=self.cfg.find_unused_parameters  
        )   

        del teacher_cfg     

        # 初始化学习率调度器
        self.self_lr_scheduler = False 
        if args.lrsheduler is not None:
            iter_per_epoch = len(self.train_dataloader)
            logger.info("     ## Using Self-defined Scheduler-{} ## ".format(args.lrsheduler))
            self.lr_scheduler = FlatCosineLRScheduler(self.optimizer, args.lr_gamma, iter_per_epoch, total_epochs=args.epoches,  
                                                warmup_iter=args.warmup_iter, flat_epochs=args.flat_epoch, no_aug_epochs=args.no_aug_epoch, lr_scyedule_save_path=self.output_dir)
            self.self_lr_scheduler = True

        # 统计需要训练的参数数量 
        n_parameters = sum([p.numel() for p in self.model.parameters() if p.requires_grad])
        logger.info(f'number of trainable parameters: {n_parameters}')  
 
        feature_distill_criterion, logical_distill_criterion = None, None 
     
        # 特征蒸馏
        s_featureExt, t_featureExt = None, None
        if args.kd_loss_type in ['feature', 'all']: 
            logger.info(RED + '------------------- feature distill check!!!!! -------------------' + RESET)
            logger.info(RED + f'feature distill select: {args.feature_loss_type}' + RESET)  
            s_kd_layers, t_kd_layers = args.student_kd_layers, args.teacher_kd_layers
            s_featureExt, t_featureExt = FeatureExtractor(student_is_Ultralytics), FeatureExtractor(teacher_is_Ultralytics)
            s_featureExt.register_hooks(self.model, s_kd_layers)  
            t_featureExt.register_hooks(self.teacher_model, t_kd_layers)
            
            # base_size = self.cfg.train_dataloader.collate_fn.base_size
            inputs = torch.randn((2, 3, *self.cfg.yaml_cfg['eval_spatial_size'])).to(self.device)
            self.model.eval()
            self.teacher_model.eval()    
            with torch.no_grad():
                _ = self.teacher_model(inputs)     
                _ = self.model(inputs)
            s_feature, t_feature = s_featureExt.get_features_in_order(), t_featureExt.get_features_in_order()

            del inputs, _     
            
            logger.info(RED + '------------------- student layer info -------------------' + RESET)     
            for layer_name, feature in zip(s_kd_layers, s_feature):  
                print(ORANGE + 'layer_name:' + GREEN + layer_name  + '   ' + ORANGE + 'feature_size:' + GREEN + f'{feature.size()}' + RESET)    
            
            logger.info(RED + '------------------- teacher layer info -------------------' + RESET) 
            for layer_name, feature in zip(t_kd_layers, t_feature):     
                print(ORANGE + 'layer_name:' + GREEN + layer_name + '   ' + ORANGE + 'feature_size:' + GREEN + f'{feature.size()}' + RESET)   
  
            check_feature_map_ok = True     
            logger.info(RED + "Check whether the levels of teachers and students match" + RESET)
            for s_layer_name, s_fea, t_layer_name, t_fea in zip(s_kd_layers, s_feature, t_kd_layers, t_feature):   
                if s_fea.size(2) != t_fea.size(2) or s_fea.size(3) != t_fea.size(3):
                    logger.info(ORANGE + 'student_layer_name:' + GREEN +  f'{s_layer_name}-[{s_fea.size(2)},{s_fea.size(3)}]  ' + ORANGE + 't_layer_name:' + GREEN + f'{t_layer_name}-[{t_fea.size(2)},{t_fea.size(3)}]  ' + RESET + 'featuremap size not match! please check.❌')
                    check_feature_map_ok = False    
                else:    
                    logger.info(ORANGE + 'student_layer_name:' + GREEN +  f'{s_layer_name}-[{s_fea.size(2)},{s_fea.size(3)}]  ' + ORANGE + 't_layer_name:' + GREEN + f'{t_layer_name}-[{t_fea.size(2)},{t_fea.size(3)}]  ' + RESET + 'featuremap size match!✅') 

            if not check_feature_map_ok:  
                raise Exception(f'Please check the corresponding layers of the teacher model and the student model.')
            
            feature_distill_criterion = FeatureLoss([_.size(1) for _ in s_feature], [_.size(1) for _ in t_feature], args.feature_loss_type).to(self.device)   
            s_featureExt.remove_hooks()   
            t_featureExt.remove_hooks()

            logger.info(RED + '------------------- feature distill check finish!!!!! -------------------' + RESET)    
     
        if args.kd_loss_type in ['logical', 'all']:     
            logger.info(RED + '------------------- logical distill check!!!!! -------------------' + RESET)  
            logger.info(RED + f'logical distill select: {args.logical_loss_type}' + RESET)
   
            backup_dataloader = copy.deepcopy(self.train_dataloader)
            inputs, targets = next(iter(backup_dataloader))
            inputs, targets = inputs.to(self.device), [{k: v.to(self.device, non_blocking=True) for k, v in t.items()} for t in targets]    
            self.model.train()
            self.teacher_model.train()   
            with torch.no_grad():
                t_pred = self.teacher_model(inputs, targets=targets)  
                s_pred = self.model(inputs, targets=targets)
   
            del backup_dataloader, inputs, targets

            logger.info(RED + f'student classes:{s_pred["pred_logits"].size(-1)} | teacher classes:{t_pred["pred_logits"].size(-1)}' + RESET)  
            if s_pred['pred_logits'].size(-1) != t_pred['pred_logits'].size(-1): 
                raise Exception('The number of classifications of the teacher model and the student model does not match. Please check the weights.') 

            if s_pred['pred_logits'].size(-2) != t_pred['pred_logits'].size(-2):
                raise Exception('The number of Queries of the teacher model and the student model does not match. Please check the model.') 

            if args.logical_loss_type == 'single':  
                logical_distill_criterion = DETRLogicLoss(self.device)  
            elif args.logical_loss_type == 'mutil':  
                pre_outputs_distill_ratio = -1 # 初始化
                aux_outputs_distill_ratio = 0.5
                pred_outputs_distill_ratio = 1.0    
                if 'pre_outputs' in s_pred and 'pre_outputs' in t_pred:
                    pre_outputs_distill_ratio = 0.2 # 如果输出中有pre_outputs的key，就设定为0.2
    
                t_aux_len, s_aux_len = len(t_pred['aux_outputs']), len(s_pred['aux_outputs']) 
                logger.info(RED + f'student aux head len:{s_aux_len} | teacher aux head len:{t_aux_len}' + RESET)   
                if t_aux_len != s_aux_len:
                    raise Exception('The Aux layer numbers of the teacher model and the student model do not match.')
                
                logical_distill_criterion = DETRMutilDecoderLogicLoss(pre_outputs_distill_ratio, 
                                                                      aux_outputs_distill_ratio,
                                                                      s_aux_len, 
                                                                      pred_outputs_distill_ratio, 
                                                                      self.device)    
            else:
                raise Exception(f'logical_loss_type param illegal. {args.logical_loss_type} not in [single, mutil]') 
    
            logger.info(RED + '------------------- logical distill check finish!!!!! -------------------' + RESET)    

        best_stat = {'epoch': -1, }
        # evaluate again before resume training
        if self.last_epoch > 0:
            module = self.ema.module if self.ema else self.model
            test_stats, coco_evaluator = evaluate(    
                module,     
                self.criterion, 
                self.postprocessor,    
                self.val_dataloader,
                self.evaluator,    
                self.device,    
                yolo_metrice=self.cfg.yolo_metrice     
            )
            if test_stats: 
                # 收集所有指标并计算平均值     
                metrics = {k: test_stats[k][0] for k in test_stats}
                avg_metric = sum(metrics.values()) / len(metrics)
                
                # 初始化best_stat
                best_stat['epoch'] = self.last_epoch   
                best_stat['avg_metric'] = avg_metric
                best_stat.update(metrics)   
  
                logger.info(f'Resume from epoch {self.last_epoch}:')
                logger.info(f'  Avg metric: {avg_metric:.4f}')   
                for k, v in metrics.items():   
                    logger.info(f'  {k}: {v:.4f}')
                logger.info(f'best_stat: {best_stat}')
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
     
        distill_flag = True
        start_time = time.time()    
        start_epoch = self.last_epoch + 1   
        for epoch in range(start_epoch, args.epoches): 

            self.train_dataloader.set_epoch(epoch)
            self.criterion.set_epoch(epoch)
            # self.train_dataloader.dataset.set_epoch(epoch)
            if dist_utils.is_dist_available_and_initialized():
                self.train_dataloader.sampler.set_epoch(epoch)

            if epoch == self.train_dataloader.collate_fn.stop_epoch:
                self.load_resume_state(str(self.output_dir / 'best_stg1.pth'))
                self.ema.decay = self.train_dataloader.collate_fn.ema_restart_decay   
                logger.info(f'Refresh EMA at epoch {epoch} with decay {self.ema.decay}') 
            
            if distill_epoch == epoch and self.cfg.kd_loss_epoch < 1.0:    
                logger.info(RED + f'Epoch:[{epoch}] Close Distillation Learning.' + RESET)
                distill_flag = False 

            if args.kd_loss_type in ['feature', 'all'] and distill_flag: 
                s_featureExt.register_hooks(self.model, s_kd_layers)
                t_featureExt.register_hooks(self.teacher_model, t_kd_layers)  

            # 蒸馏一个 epoch  
            train_stats = distill_one_epoch(
                self.self_lr_scheduler,
                self.lr_scheduler,
                self.model,
                self.teacher_model,
                s_featureExt, 
                t_featureExt,    
                self.criterion, 
                feature_distill_criterion if distill_flag else None, 
                logical_distill_criterion if distill_flag else None,     
                self.train_dataloader,   
                self.optimizer,  
                self.device, 
                epoch,  
                max_norm=args.clip_max_norm, 
                print_freq=args.print_freq, 
                ema=self.ema,    
                scaler=self.scaler, 
                lr_warmup_scheduler=self.lr_warmup_scheduler,    
                writer=self.writer,
                plot_train_batch_freq=args.plot_train_batch_freq,   
                output_dir=self.output_dir,
                epoches=args.epoches, # 总的训练次数    
                verbose_type=args.verbose_type,
                feature_loss_ratio=args.feature_loss_ratio, # 特征蒸馏的损失系数  
                logical_loss_ratio=args.logical_loss_ratio, # 逻辑蒸馏的损失系数
                distill_loss_decay=args.kd_loss_decay # 蒸馏损失的调度方法
            )
     
            if torch.cuda.is_available():    
                torch.cuda.empty_cache()
                gc.collect()

            if not self.self_lr_scheduler:  # update by epoch     
                if self.lr_warmup_scheduler is None or self.lr_warmup_scheduler.finished():  
                    self.lr_scheduler.step()
   
            self.last_epoch += 1

            if self.output_dir and epoch < self.train_dataloader.collate_fn.stop_epoch:
                checkpoint_paths = [self.output_dir / 'last.pth']     
                # extra checkpoint before LR drop and every 100 epochs     
                if (epoch + 1) % args.checkpoint_freq == 0:   
                    checkpoint_paths.append(self.output_dir / f'checkpoint{epoch:04}.pth')
                with ModelSaverFunc(self):
                    for checkpoint_path in checkpoint_paths:   
                        dist_utils.save_on_master(self.state_dict(), checkpoint_path)

            # 训练一个epoch后计算模型指标     
            module = self.ema.module if self.ema else self.model     
            test_stats, coco_evaluator = evaluate( 
                module,
                self.criterion,     
                self.postprocessor,
                self.val_dataloader,
                self.evaluator,
                self.device,
                yolo_metrice=self.cfg.yolo_metrice
            )  
    
            if torch.cuda.is_available():  
                torch.cuda.empty_cache()
                gc.collect()

            if args.kd_loss_type in ['feature', 'all'] and distill_flag:
                s_featureExt.remove_hooks()
                t_featureExt.remove_hooks()

            best_stat = self.save_best_model(test_stats, best_stat, epoch)  

            log_stats = { 
                **{f'train_{k}': v for k, v in train_stats.items()},    
                **{f'test_{k}': v for k, v in test_stats.items()},
                'epoch': epoch, 
                'n_parameters': n_parameters   
            }
 
            if self.output_dir and dist_utils.is_main_process():
                with (self.output_dir / "log.txt").open("a") as f:    
                    f.write(json.dumps(log_stats) + "\n")    
    
                # for evaluation logs
                # if coco_evaluator is not None:     
                #     (self.output_dir / 'eval').mkdir(exist_ok=True)
                #     if "bbox" in coco_evaluator.coco_eval:
                #         filenames = ['latest.pth']     
                #         if epoch % 50 == 0:     
                #             filenames.append(f'{epoch:03}.pth')   
                #         for name in filenames:
                #             torch.save(coco_evaluator.coco_eval["bbox"].eval,
                #                     self.output_dir / "eval" / name)

        total_time = time.time() - start_time     
        total_time_str = str(datetime.timedelta(seconds=int(total_time)))
        logger.info('Training time {}'.format(total_time_str))  
    
    def save_best_model(self, test_stats, best_stat, epoch):  
        if test_stats:
            # 计算所有评判标准的平均AP（用于判断最佳模型）  
            all_metrics = []
            metric_names = []
            for k in test_stats:
                if self.writer and dist_utils.is_main_process():  
                    for i, v in enumerate(test_stats[k]):   
                        if self.evaluator.using_tiny_metrice:   
                            self.writer.add_scalar(f'Test/{k}_{coco_name_tiny_list[i]}', v, epoch)
                        else:  
                            self.writer.add_scalar(f'Test/{k}_{coco_name_list[i]}', v, epoch)    
   
                all_metrics.append(test_stats[k][0]) # 0代表选择ap50-95 1代表选择ap50
                metric_names.append(k)    
   
            # 计算平均指标
            avg_metric = sum(all_metrics) / len(all_metrics) if all_metrics else 0
  
            # 初始化best_stat
            if 'avg_metric' not in best_stat:
                best_stat['avg_metric'] = 0  
                best_stat['epoch'] = -1  
                # 为每个指标初始化 
                for k in metric_names:    
                    best_stat[k] = 0
            
            # 保存旧的最佳值（用于日志输出）  
            best_stat_temp = best_stat.copy() 

            # 判断是否是新的最佳模型     
            is_best = avg_metric > best_stat['avg_metric']     
  
            if is_best:
                best_stat['epoch'] = epoch 
                best_stat['avg_metric'] = avg_metric
                # 更新每个指标的最佳值   
                for k, metric_val in zip(metric_names, all_metrics):
                    best_stat[k] = metric_val
    
            # 日志输出
            logger.info(f'Current metrics: {dict(zip(metric_names, all_metrics))}')     
            logger.info(f'Current avg: {avg_metric:.4f}, Best avg: {best_stat["avg_metric"]:.4f} (epoch {best_stat["epoch"]})')
   
            # 保存最佳模型
            if is_best and self.output_dir:
                logger.info(RED + f"🎉 New Best Model!" + RESET)
                logger.info(RED + f"  Epoch: {best_stat_temp['epoch']} -> {best_stat['epoch']}" + RESET)    
                logger.info(RED + f"  Avg AP: {best_stat_temp.get('avg_metric', 0):.4f} -> {best_stat['avg_metric']:.4f}" + RESET)
                
                # 打印每个指标的变化
                for k in metric_names: 
                    old_val = best_stat_temp.get(k, 0)     
                    new_val = best_stat[k]
                    logger.info(RED + f"  {k}: {old_val:.4f} -> {new_val:.4f}" + RESET)
    
                with ModelSaverFunc(self):
                    # 根据训练阶段保存不同的模型
                    if epoch >= self.train_dataloader.collate_fn.stop_epoch:
                        save_path = self.output_dir / f'best_stg2.pth'   
                        dist_utils.save_on_master(self.state_dict(), save_path)
                        logger.info(RED + f"💾 Saved best_stg2.pth" + RESET)
                    else:
                        save_path = self.output_dir / f'best_stg1.pth'
                        dist_utils.save_on_master(self.state_dict(), save_path)
                        logger.info(RED + f"💾 Saved best_stg1.pth" + RESET)
     
            # Stage 2 开始时的特殊处理
            elif epoch >= self.train_dataloader.collate_fn.stop_epoch and epoch == self.train_dataloader.collate_fn.stop_epoch:
                self.ema.decay -= 0.0001  # 衰减因子变小意味着当前模型参数在EMA更新中的占比更大
                stg1_model_path = self.output_dir / f'best_stg1.pth'    
                self.load_resume_state(str(stg1_model_path)) 
                logger.info(f'🔄 Refresh EMA at epoch {epoch} with decay {self.ema.decay}')   
 
        return best_stat     
