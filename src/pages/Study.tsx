import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Volume2, X, Check, Mic, Play } from 'lucide-react';
import * as Progress from '@radix-ui/react-progress';

const VOCAB_DATA = [
  { id: 1, word: 'Negotiation', phonetic: '/nɪˌɡoʊʃiˈeɪʃn/', translation: 'n. 谈判，协商', example: 'The negotiation was successful.', type: 'vocab' },
  { id: 2, word: 'Implement', phonetic: '/ˈɪmplɪment/', translation: 'v. 实施，执行', example: 'We need to implement the new policy.', type: 'vocab' },
  { id: 3, word: 'Colleague', phonetic: '/ˈkɑːliːɡ/', translation: 'n. 同事，同僚', example: 'She is a former colleague of mine.', type: 'vocab' },
];

const Study = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [progress, setProgress] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const currentCard = VOCAB_DATA[currentIndex];

  const handleNext = () => {
    setIsFlipped(false);
    
    // Animate out and then next
    setTimeout(() => {
      const nextProgress = ((currentIndex + 1) / VOCAB_DATA.length) * 100;
      setProgress(nextProgress);
      
      if (currentIndex < VOCAB_DATA.length - 1) {
        setCurrentIndex(prev => prev + 1);
      } else {
        setCompleted(true);
      }
    }, 200);
  };

  if (completed) {
    return (
      <div className="h-full flex flex-col items-center justify-center space-y-6">
        <motion.div 
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="w-32 h-32 bg-primary/20 rounded-full flex items-center justify-center text-primary mb-4"
        >
          <Check size={64} />
        </motion.div>
        <h2 className="text-3xl font-bold text-white">太棒了！</h2>
        <p className="text-muted-foreground">你已经完成了今天的学习任务</p>
        <div className="flex gap-4 pt-8">
          <button className="px-8 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-white font-medium transition-colors">
            再学一遍
          </button>
          <button className="px-8 py-3 rounded-xl bg-primary hover:bg-primary-hover text-white font-medium transition-colors shadow-[0_0_20px_rgba(139,92,246,0.4)]">
            返回仪表盘
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto h-full flex flex-col pb-10">
      {/* Top Header */}
      <div className="flex items-center gap-6 mb-8">
        <button className="p-2 rounded-full hover:bg-white/5 transition-colors text-muted-foreground">
          <X size={24} />
        </button>
        <div className="flex-1">
          <Progress.Root className="h-3 w-full overflow-hidden rounded-full bg-white/10" value={progress}>
            <Progress.Indicator 
              className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-500 ease-out rounded-full" 
              style={{ width: `${progress}%` }} 
            />
          </Progress.Root>
        </div>
        <span className="text-sm font-medium text-muted-foreground w-12 text-right">
          {currentIndex + 1} / {VOCAB_DATA.length}
        </span>
      </div>

      {/* Main Card Area */}
      <div className="flex-1 flex flex-col items-center justify-center relative perspective-1000">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ x: 50, opacity: 0, rotateY: isFlipped ? 180 : 0 }}
            animate={{ x: 0, opacity: 1, rotateY: isFlipped ? 180 : 0 }}
            exit={{ x: -50, opacity: 0, transition: { duration: 0.2 } }}
            transition={{ duration: 0.5, type: 'spring', stiffness: 200, damping: 20 }}
            onClick={() => setIsFlipped(!isFlipped)}
            className="w-full max-w-md aspect-[3/4] cursor-pointer transform-style-3d relative"
            style={{ transformStyle: 'preserve-3d' }}
          >
            {/* Front of card */}
            <div 
              className="absolute inset-0 glass-panel rounded-3xl p-8 flex flex-col items-center justify-center text-center backface-hidden shadow-2xl border-white/20"
              style={{ backfaceVisibility: 'hidden' }}
            >
              <h2 className="text-5xl font-bold text-white mb-6">{currentCard.word}</h2>
              <p className="text-xl text-primary font-medium mb-8 tracking-wider">{currentCard.phonetic}</p>
              
              <button 
                onClick={(e) => { e.stopPropagation(); /* Play sound */ }}
                className="w-16 h-16 rounded-full bg-white/5 hover:bg-primary/20 flex items-center justify-center text-white transition-colors mt-auto"
              >
                <Volume2 size={28} />
              </button>
              
              <p className="text-sm text-muted-foreground mt-8">点击卡片翻转</p>
            </div>

            {/* Back of card */}
            <div 
              className="absolute inset-0 glass-panel rounded-3xl p-8 flex flex-col items-center justify-center text-center backface-hidden shadow-2xl border-white/20 bg-gradient-to-b from-primary/10 to-transparent"
              style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
            >
              <h3 className="text-3xl font-bold text-white mb-6">{currentCard.translation}</h3>
              
              <div className="w-full h-px bg-white/10 my-6"></div>
              
              <div className="text-left w-full space-y-2 mb-8">
                <p className="text-sm text-muted-foreground">例句：</p>
                <p className="text-lg text-white leading-relaxed">{currentCard.example}</p>
              </div>

              <div className="mt-auto w-full flex justify-center gap-4">
                <button 
                  onClick={(e) => { e.stopPropagation(); /* Play sound */ }}
                  className="w-12 h-12 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white transition-colors"
                >
                  <Play size={20} />
                </button>
                <button 
                  onClick={(e) => { 
                    e.stopPropagation(); 
                    setIsRecording(!isRecording);
                  }}
                  className={`w-12 h-12 rounded-full flex items-center justify-center text-white transition-colors ${isRecording ? 'bg-red-500 animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.5)]' : 'bg-white/5 hover:bg-white/10'}`}
                >
                  <Mic size={20} />
                </button>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Bottom Actions */}
      <div className="mt-12 flex items-center justify-center gap-6">
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => handleNext()}
          className="w-36 py-4 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium transition-colors"
        >
          不认识
        </motion.button>
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => handleNext()}
          className="w-36 py-4 rounded-2xl bg-secondary hover:bg-secondary/90 text-white font-bold transition-colors shadow-[0_0_20px_rgba(20,184,166,0.3)] hover:shadow-[0_0_30px_rgba(20,184,166,0.5)]"
        >
          认识
        </motion.button>
      </div>
    </div>
  );
};

export default Study;