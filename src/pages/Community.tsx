import { useState } from 'react';
import { motion } from 'framer-motion';
import { Heart, MessageCircle, Share2, Award, TrendingUp } from 'lucide-react';

const POSTS = [
  {
    id: 1,
    user: { name: 'Sarah W.', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah&backgroundColor=ec4899' },
    content: 'Just finished the "Business English" module! The negotiation simulation was incredibly realistic. Highly recommend to anyone preparing for international meetings. 🚀',
    lang: '英语',
    likes: 24,
    comments: 5,
    time: '2 小时前',
    isLiked: false
  },
  {
    id: 2,
    user: { name: 'Kenji T.', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Kenji&backgroundColor=3b82f6' },
    content: 'N5の勉強を始めました！五十音図は難しいですが、頑張ります。皆さん、よろしくお願いします！🎌',
    lang: '日语',
    likes: 156,
    comments: 12,
    time: '5 小时前',
    isLiked: true
  },
  {
    id: 3,
    user: { name: 'Emma L.', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Emma&backgroundColor=10b981' },
    content: 'Can someone explain the difference between "affect" and "effect"? I always get them confused in writing exercises. 😅',
    lang: '英语',
    likes: 8,
    comments: 14,
    time: '1 天前',
    isLiked: false
  }
];

const LEADERBOARD = [
  { rank: 1, name: 'David K.', xp: 2450, change: 'up' },
  { rank: 2, name: 'Alex C.', xp: 2120, change: 'up' },
  { rank: 3, name: 'Maria S.', xp: 1980, change: 'down' },
  { rank: 4, name: 'Yuki M.', xp: 1850, change: 'same' },
  { rank: 5, name: 'John D.', xp: 1720, change: 'up' },
];

const Community = () => {
  const [posts, setPosts] = useState(POSTS);

  const toggleLike = (id: number) => {
    setPosts(posts.map(p => {
      if (p.id === id) {
        return { ...p, isLiked: !p.isLiked, likes: p.isLiked ? p.likes - 1 : p.likes + 1 };
      }
      return p;
    }));
  };

  return (
    <div className="flex flex-col lg:flex-row gap-8 pb-10">
      {/* Main Feed */}
      <div className="flex-1 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-white">社区动态</h1>
          <button className="px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl font-medium transition-colors text-sm shadow-[0_0_15px_rgba(139,92,246,0.3)]">
            发布动态
          </button>
        </div>

        {/* Create Post Input */}
        <div className="glass-panel p-4 rounded-2xl flex gap-4">
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex&backgroundColor=8b5cf6" alt="You" className="w-10 h-10 rounded-full" />
          <div className="flex-1">
            <textarea 
              placeholder="分享你的学习心得或提出问题..." 
              className="w-full bg-transparent border-none resize-none focus:outline-none text-foreground placeholder:text-muted-foreground min-h-[80px]"
            ></textarea>
            <div className="flex justify-between items-center pt-2 border-t border-white/10">
              <div className="flex gap-2">
                <span className="text-xs px-2 py-1 rounded-md bg-white/5 text-muted-foreground cursor-pointer hover:bg-white/10"># 标签</span>
                <span className="text-xs px-2 py-1 rounded-md bg-white/5 text-muted-foreground cursor-pointer hover:bg-white/10">@ 提到</span>
              </div>
              <button className="px-4 py-1.5 bg-primary/20 text-primary hover:bg-primary/30 rounded-lg text-sm font-medium transition-colors">
                发布
              </button>
            </div>
          </div>
        </div>

        {/* Feed List */}
        <div className="space-y-4">
          {posts.map((post) => (
            <motion.div 
              key={post.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-panel p-5 rounded-2xl"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-3">
                  <img src={post.user.avatar} alt={post.user.name} className="w-10 h-10 rounded-full bg-white/10" />
                  <div>
                    <h4 className="font-bold text-white text-sm">{post.user.name}</h4>
                    <p className="text-xs text-muted-foreground">{post.time} · {post.lang}</p>
                  </div>
                </div>
                <button className="text-muted-foreground hover:text-white">...</button>
              </div>
              
              <p className="text-foreground text-sm leading-relaxed mb-4">
                {post.content}
              </p>
              
              <div className="flex items-center gap-6 border-t border-white/5 pt-3">
                <button 
                  onClick={() => toggleLike(post.id)}
                  className={`flex items-center gap-1.5 text-xs font-medium transition-colors ${post.isLiked ? 'text-pink-500' : 'text-muted-foreground hover:text-white'}`}
                >
                  <motion.div whileTap={{ scale: 1.5 }}>
                    <Heart size={16} fill={post.isLiked ? 'currentColor' : 'none'} />
                  </motion.div>
                  {post.likes}
                </button>
                <button className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-white transition-colors">
                  <MessageCircle size={16} />
                  {post.comments}
                </button>
                <button className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-white transition-colors">
                  <Share2 size={16} />
                  分享
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Sidebar: Leaderboard */}
      <div className="w-full lg:w-80 space-y-6">
        <div className="glass-panel p-5 rounded-2xl">
          <div className="flex items-center gap-2 mb-6">
            <div className="p-2 rounded-lg bg-orange-500/20 text-orange-500">
              <Award size={20} />
            </div>
            <h3 className="font-bold text-lg text-white">本周排行榜</h3>
          </div>
          
          <div className="space-y-4">
            {LEADERBOARD.map((user, i) => (
              <div key={user.rank} className="flex items-center justify-between group">
                <div className="flex items-center gap-3">
                  <div className={`w-6 text-center font-bold text-sm ${i === 0 ? 'text-yellow-400' : i === 1 ? 'text-gray-300' : i === 2 ? 'text-amber-600' : 'text-muted-foreground'}`}>
                    {user.rank}
                  </div>
                  <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}&backgroundColor=transparent`} alt={user.name} className="w-8 h-8 rounded-full bg-white/10" />
                  <span className={`text-sm font-medium ${user.name === 'Alex C.' ? 'text-primary' : 'text-white'}`}>
                    {user.name} {user.name === 'Alex C.' && '(你)'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-muted-foreground">{user.xp} XP</span>
                  {user.change === 'up' && <TrendingUp size={14} className="text-green-500" />}
                  {user.change === 'down' && <TrendingUp size={14} className="text-red-500 transform rotate-180" />}
                  {user.change === 'same' && <div className="w-3.5 h-0.5 bg-gray-500 rounded"></div>}
                </div>
              </div>
            ))}
          </div>
          
          <button className="w-full mt-6 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-medium text-white transition-colors">
            查看完整榜单
          </button>
        </div>
      </div>
    </div>
  );
};

export default Community;