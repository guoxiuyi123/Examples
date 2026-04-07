import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, Star, Clock, BookOpen } from 'lucide-react';
import * as Tabs from '@radix-ui/react-tabs';

const LANGUAGES = [
  { id: 'en', name: '英语', icon: '🇺🇸' },
  { id: 'ja', name: '日语', icon: '🇯🇵' },
  { id: 'ko', name: '韩语', icon: '🇰🇷' },
  { id: 'es', name: '西班牙语', icon: '🇪🇸' },
  { id: 'fr', name: '法语', icon: '🇫🇷' },
];

const LEVELS = ['全部', '入门 (A1)', '初级 (A2)', '中级 (B1)', '中高级 (B2)', '高级 (C1)'];

const COURSES = [
  { id: 1, lang: 'en', level: '中级 (B1)', title: '商务英语实战：从会议到谈判', desc: '掌握职场核心词汇，提升跨文化沟通能力', rating: 4.9, students: '1.2w', duration: '20课时', image: 'https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=800&q=80' },
  { id: 2, lang: 'en', level: '初级 (A2)', title: '日常情景对话 100 篇', desc: '最实用的生活英语，解决出国旅游、购物点餐难题', rating: 4.8, students: '3.5w', duration: '15课时', image: 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80' },
  { id: 3, lang: 'ja', level: '入门 (A1)', title: '零基础五十音图速记', desc: '通过图像联想法，1小时掌握平假名和片假名', rating: 4.9, students: '5.2w', duration: '5课时', image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=800&q=80' },
  { id: 4, lang: 'ja', level: '中级 (B1)', title: '动漫日语：听懂原声无压力', desc: '精选热门动漫片段，学习地道年轻人口语', rating: 4.7, students: '2.1w', duration: '12课时', image: 'https://images.unsplash.com/photo-1578305698822-550974f14e21?auto=format&fit=crop&w=800&q=80' },
  { id: 5, lang: 'ko', level: '初级 (A2)', title: '韩剧高频口语100句', desc: '精选热门韩剧原声，教你地道的生活表达', rating: 4.8, students: '1.8w', duration: '10课时', image: 'https://images.unsplash.com/photo-1580214157870-7b56dc632a82?auto=format&fit=crop&w=800&q=80' },
  { id: 6, lang: 'en', level: '高级 (C1)', title: 'TED 演讲精听精读', desc: '提升高级听力与词汇量，拓展思维深度', rating: 4.9, students: '8.9k', duration: '30课时', image: 'https://images.unsplash.com/photo-1475721028070-28122049f7bb?auto=format&fit=crop&w=800&q=80' },
];

const Courses = () => {
  const [activeLang, setActiveLang] = useState('en');
  const [activeLevel, setActiveLevel] = useState('全部');

  const filteredCourses = COURSES.filter(c => 
    c.lang === activeLang && 
    (activeLevel === '全部' || c.level === activeLevel)
  );

  return (
    <div className="space-y-8 pb-10">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-2">
          <h1 className="text-3xl md:text-4xl font-bold text-white">探索课程 🌍</h1>
          <p className="text-muted-foreground">发现适合你的语言课程，开启新的学习旅程。</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary" size={18} />
            <input 
              type="text" 
              placeholder="搜索课程名称..." 
              className="w-full md:w-64 bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>
          <button className="p-2.5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors text-white">
            <Filter size={18} />
          </button>
        </div>
      </div>

      <Tabs.Root value={activeLang} onValueChange={setActiveLang} className="space-y-6">
        <Tabs.List className="flex overflow-x-auto custom-scrollbar pb-2 gap-2 border-b border-white/10">
          {LANGUAGES.map(lang => (
            <Tabs.Trigger 
              key={lang.id} 
              value={lang.id}
              className="flex items-center gap-2 px-5 py-3 rounded-t-xl text-sm font-medium transition-all data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:border-b-2 data-[state=active]:border-primary text-muted-foreground hover:text-white whitespace-nowrap"
            >
              <span>{lang.icon}</span>
              {lang.name}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <div className="flex flex-wrap gap-2">
          {LEVELS.map(level => (
            <button
              key={level}
              onClick={() => setActiveLevel(level)}
              className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all border ${
                activeLevel === level 
                  ? 'bg-secondary text-white border-secondary shadow-[0_0_10px_rgba(20,184,166,0.3)]' 
                  : 'bg-white/5 text-muted-foreground border-white/10 hover:bg-white/10 hover:text-white'
              }`}
            >
              {level}
            </button>
          ))}
        </div>

        <div className="relative min-h-[400px]">
          <AnimatePresence mode="popLayout">
            <motion.div
              key={`${activeLang}-${activeLevel}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
            >
              {filteredCourses.length > 0 ? (
                filteredCourses.map((course, idx) => (
                  <motion.div 
                    key={course.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.05 }}
                    className="glass-panel rounded-2xl overflow-hidden group cursor-pointer hover:-translate-y-1 transition-all duration-300 border border-white/10 hover:border-primary/30"
                  >
                    <div className="h-48 relative overflow-hidden">
                      <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors z-10" />
                      <img 
                        src={course.image} 
                        alt={course.title} 
                        className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-700"
                      />
                      <div className="absolute top-3 left-3 z-20">
                        <span className="px-2.5 py-1 bg-black/60 backdrop-blur-md rounded-lg text-xs font-medium text-white border border-white/10">
                          {course.level}
                        </span>
                      </div>
                    </div>
                    
                    <div className="p-5 space-y-4">
                      <div>
                        <h3 className="text-lg font-bold text-white group-hover:text-primary transition-colors line-clamp-1">{course.title}</h3>
                        <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{course.desc}</p>
                      </div>
                      
                      <div className="flex items-center justify-between pt-2 border-t border-white/5">
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Star size={14} className="text-accent" fill="currentColor" />
                            <span className="text-white font-medium">{course.rating}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <BookOpen size={14} />
                            <span>{course.students}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock size={14} />
                          <span>{course.duration}</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="col-span-full flex flex-col items-center justify-center py-20 text-muted-foreground">
                  <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
                    <Search size={24} className="opacity-50" />
                  </div>
                  <p>没有找到符合条件的课程</p>
                  <button 
                    onClick={() => setActiveLevel('全部')}
                    className="mt-4 text-primary hover:text-primary-hover text-sm font-medium"
                  >
                    清除筛选条件
                  </button>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </Tabs.Root>
    </div>
  );
};

export default Courses;