import { motion } from 'framer-motion';
import { Play, Flame, Target, ArrowRight, User } from 'lucide-react';
import { useStore } from '../store';

const CircularProgress = ({ percentage, color = 'stroke-primary', size = 120, strokeWidth = 8 }: { percentage: number, color?: string, size?: number, strokeWidth?: number }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle
          className="stroke-muted/30"
          strokeWidth={strokeWidth}
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        <motion.circle
          className={`${color} transition-all duration-1000 ease-out`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white">{percentage}%</span>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const user = useStore(state => state.user);

  return (
    <div className="space-y-8 pb-10">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-1"
        >
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white">欢迎回来，{user?.name?.split(' ')[0]} 👋</h1>
          <p className="text-muted-foreground text-sm md:text-base">你已经连续学习 <span className="text-accent font-bold">{user?.streak}</span> 天了，继续保持！</p>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="flex items-center gap-4 bg-white/5 p-3 rounded-2xl border border-white/10"
        >
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center text-orange-500">
              <Flame size={20} />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">当前连击</p>
              <p className="text-sm font-bold text-white">{user?.streak} 天</p>
            </div>
          </div>
          <div className="w-px h-8 bg-white/10"></div>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary">
              <Target size={20} />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">今日目标</p>
              <p className="text-sm font-bold text-white">35 / 50 XP</p>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Progress Card */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 glass-panel rounded-3xl p-6 relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4"></div>
          
          <div className="flex flex-col md:flex-row gap-8 items-center relative z-10">
            <div className="flex-1 space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary/20 text-secondary text-xs font-medium border border-secondary/20">
                <span>🇺🇸 英语 - 中级 (B1)</span>
              </div>
              <h2 className="text-2xl font-bold text-white">日常交流与职场词汇</h2>
              <p className="text-muted-foreground text-sm">
                你正在学习第 4 单元：商务会议沟通技巧。掌握这部分内容将帮助你在全英文会议中流利表达。
              </p>
              
              <div className="pt-4 flex gap-3">
                <button className="flex items-center gap-2 px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-xl font-medium transition-all shadow-[0_0_20px_rgba(139,92,246,0.4)] hover:shadow-[0_0_30px_rgba(139,92,246,0.6)]">
                  <Play size={18} fill="currentColor" />
                  继续学习
                </button>
                <button className="px-6 py-3 bg-white/5 hover:bg-white/10 text-white rounded-xl font-medium transition-colors border border-white/10">
                  复习生词
                </button>
              </div>
            </div>
            
            <div className="flex-shrink-0">
              <CircularProgress percentage={68} size={160} strokeWidth={12} color="stroke-secondary" />
              <p className="text-center text-xs text-muted-foreground mt-4 font-medium">单元进度</p>
            </div>
          </div>
        </motion.div>

        {/* Daily Tasks */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-panel rounded-3xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-white">今日任务</h3>
            <span className="text-xs font-medium text-muted-foreground bg-white/5 px-2 py-1 rounded-md">2/4 完成</span>
          </div>
          
          <div className="space-y-3">
            {[
              { title: "完成 1 个新课时", xp: 15, done: true },
              { title: "复习 20 个单词", xp: 10, done: true },
              { title: "进行 5 分钟口语练习", xp: 15, done: false },
              { title: "阅读一篇外文短文", xp: 10, done: false },
            ].map((task, i) => (
              <div key={i} className={`flex items-center justify-between p-3 rounded-xl border ${task.done ? 'bg-primary/10 border-primary/20' : 'bg-white/5 border-white/5'}`}>
                <div className="flex items-center gap-3">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center border ${task.done ? 'bg-primary border-primary' : 'border-muted-foreground'}`}>
                    {task.done && <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                  </div>
                  <span className={`text-sm ${task.done ? 'text-white/70 line-through' : 'text-white'}`}>{task.title}</span>
                </div>
                <span className="text-xs font-bold text-accent">+{task.xp} XP</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Recommended Courses */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white">推荐课程</h3>
          <button className="text-sm text-primary hover:text-primary-hover flex items-center gap-1 transition-colors">
            查看全部 <ArrowRight size={16} />
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { lang: "🇯🇵 日语", title: "基础五十音图速记", desc: "通过图像联想法，1小时掌握平假名和片假名", users: "1.2w", color: "from-pink-500 to-rose-500" },
            { lang: "🇰🇷 韩语", title: "韩剧高频口语100句", desc: "精选热门韩剧原声，教你地道的生活表达", users: "8.5k", color: "from-blue-500 to-cyan-500" },
            { lang: "🇬🇧 英语", title: "TED 演讲听力特训", desc: "精听精读，提升高级听力与词汇量", users: "3.4w", color: "from-amber-500 to-orange-500" }
          ].map((course, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + i * 0.1 }}
              className="glass-panel rounded-2xl overflow-hidden group cursor-pointer hover:-translate-y-1 transition-all duration-300"
            >
              <div className={`h-24 bg-gradient-to-r ${course.color} opacity-80 group-hover:opacity-100 transition-opacity flex items-center px-6`}>
                <span className="text-2xl font-bold text-white drop-shadow-md">{course.lang}</span>
              </div>
              <div className="p-5">
                <h4 className="text-lg font-bold text-white mb-2 group-hover:text-primary transition-colors">{course.title}</h4>
                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{course.desc}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <User size={14} />
                    <span>{course.users} 人在学</span>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-white group-hover:bg-primary group-hover:text-white transition-colors">
                    <ArrowRight size={16} />
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;