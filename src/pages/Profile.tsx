
import { motion } from 'framer-motion';
import { Settings, Award, Flame, Book, Clock, Star, Unlock, Lock } from 'lucide-react';

const STATS = [
  { label: '总经验值', value: '2,120', icon: Star, color: 'text-yellow-400', bg: 'bg-yellow-400/20' },
  { label: '当前连击', value: '12 天', icon: Flame, color: 'text-orange-500', bg: 'bg-orange-500/20' },
  { label: '学习时长', value: '48.5h', icon: Clock, color: 'text-blue-400', bg: 'bg-blue-400/20' },
  { label: '完成课程', value: '15', icon: Book, color: 'text-green-400', bg: 'bg-green-400/20' },
];

const ACHIEVEMENTS = [
  { id: 1, title: '初学乍练', desc: '完成第一节课程', icon: '🌱', unlocked: true, date: '2023-09-01' },
  { id: 2, title: '连击达人', desc: '连续学习 7 天', icon: '🔥', unlocked: true, date: '2023-09-08' },
  { id: 3, title: '词汇大师', desc: '掌握 500 个单词', icon: '🧠', unlocked: true, date: '2023-10-15' },
  { id: 4, title: '交际达人', desc: '在社区发布 10 条动态', icon: '💬', unlocked: false, progress: 6, total: 10 },
  { id: 5, title: '多语种天才', desc: '同时学习 3 门语言', icon: '🌍', unlocked: false, progress: 2, total: 3 },
  { id: 6, title: '学霸附体', desc: '累计获得 10,000 XP', icon: '👑', unlocked: false, progress: 2120, total: 10000 },
];

const Profile = () => {
  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-10">
      {/* Profile Header */}
      <div className="glass-panel rounded-3xl p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4"></div>
        
        <div className="flex flex-col md:flex-row items-center md:items-start gap-6 relative z-10">
          <div className="relative">
            <img 
              src="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex&backgroundColor=8b5cf6" 
              alt="Avatar" 
              className="w-24 h-24 rounded-full ring-4 ring-primary/30 p-1 object-cover bg-white/5"
            />
            <button className="absolute bottom-0 right-0 p-1.5 bg-primary text-white rounded-full hover:bg-primary-hover transition-colors">
              <Settings size={16} />
            </button>
          </div>
          
          <div className="flex-1 text-center md:text-left space-y-2">
            <div className="flex flex-col md:flex-row md:items-center gap-3">
              <h1 className="text-3xl font-bold text-white">Alex Chen</h1>
              <span className="px-3 py-1 rounded-full bg-secondary/20 text-secondary text-xs font-bold border border-secondary/20">
                Lv. 15 初学者
              </span>
            </div>
            <p className="text-muted-foreground">"语言是了解世界的另一扇窗。"</p>
            <div className="flex items-center justify-center md:justify-start gap-4 pt-2 text-sm">
              <div className="flex items-center gap-1 text-white/80">
                <span className="font-bold text-white">128</span> 关注
              </div>
              <div className="flex items-center gap-1 text-white/80">
                <span className="font-bold text-white">45</span> 粉丝
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STATS.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="glass-panel p-5 rounded-2xl flex flex-col items-center justify-center text-center gap-3"
            >
              <div className={`w-12 h-12 rounded-full ${stat.bg} flex items-center justify-center ${stat.color}`}>
                <Icon size={24} />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{stat.label}</p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Achievements Section */}
      <div>
        <div className="flex items-center gap-2 mb-6">
          <Award className="text-primary" size={24} />
          <h2 className="text-2xl font-bold text-white">成就徽章</h2>
          <span className="ml-2 text-sm text-muted-foreground font-medium bg-white/5 px-2 py-1 rounded-md">
            已解锁 3 / 6
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {ACHIEVEMENTS.map((achievement, i) => (
            <motion.div 
              key={achievement.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 + i * 0.05 }}
              className={`p-6 rounded-2xl border transition-all ${
                achievement.unlocked 
                  ? 'glass-panel border-white/10 hover:border-primary/30' 
                  : 'bg-white/5 border-white/5 opacity-70 grayscale-[0.5]'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-3xl shadow-inner ${
                  achievement.unlocked ? 'bg-gradient-to-br from-primary/20 to-secondary/20' : 'bg-white/5'
                }`}>
                  {achievement.icon}
                </div>
                {achievement.unlocked ? (
                  <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center">
                    <Unlock size={16} />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-white/10 text-muted-foreground flex items-center justify-center">
                    <Lock size={16} />
                  </div>
                )}
              </div>
              
              <h3 className={`font-bold mb-1 ${achievement.unlocked ? 'text-white' : 'text-white/70'}`}>
                {achievement.title}
              </h3>
              <p className="text-xs text-muted-foreground mb-4 h-8 line-clamp-2">
                {achievement.desc}
              </p>
              
              {achievement.unlocked ? (
                <div className="text-xs font-medium text-primary">
                  解锁于 {achievement.date}
                </div>
              ) : (
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-muted-foreground">进度</span>
                    <span className="text-white/80">{achievement.progress} / {achievement.total}</span>
                  </div>
                  <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-muted-foreground rounded-full" 
                      style={{ width: `${(achievement.progress! / achievement.total!) * 100}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Profile;