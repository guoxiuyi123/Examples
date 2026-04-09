import { Bell, Search, Settings, Menu } from "lucide-react";
import { Link } from "react-router-dom";
import { useStore } from "../../store";

const Navbar = () => {
  const user = useStore(state => state.user);

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-white/5 h-16 flex items-center justify-between px-4 md:px-8">
      {/* Mobile Menu Toggle & Brand */}
      <div className="flex md:hidden items-center gap-4">
        <button className="p-2 -ml-2 rounded-lg text-muted-foreground hover:bg-white/5 hover:text-white transition-colors">
          <Menu size={24} />
        </button>
        <Link to="/" className="font-bold text-xl tracking-wide text-gradient">
          LinguaNova
        </Link>
      </div>

      {/* Desktop Search */}
      <div className="hidden md:flex flex-1 max-w-md items-center relative group">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" size={18} />
        <input 
          type="text" 
          placeholder="搜索课程、语法、或社区动态..." 
          className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-transparent transition-all shadow-inner"
        />
      </div>

      {/* Actions & Profile */}
      <div className="flex items-center gap-3 sm:gap-5 ml-auto">
        <button className="relative p-2 rounded-full text-muted-foreground hover:text-white hover:bg-white/5 transition-all group">
          <Bell size={20} className="group-hover:animate-pulse" />
          <span className="absolute top-1.5 right-2 w-2 h-2 rounded-full bg-red-500 ring-2 ring-background"></span>
        </button>
        <button className="hidden sm:block p-2 rounded-full text-muted-foreground hover:text-white hover:bg-white/5 transition-all">
          <Settings size={20} />
        </button>
        
        <div className="h-8 w-px bg-white/10 mx-1 hidden sm:block"></div>

        <button className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="flex flex-col items-end hidden sm:flex">
            <span className="text-sm font-medium">{user?.name}</span>
            <span className="text-xs text-secondary font-medium tracking-wide">{user?.level}</span>
          </div>
          <div className="relative">
            <img 
              src={user?.avatar} 
              alt="Avatar" 
              className="w-9 h-9 rounded-full ring-2 ring-primary/30 p-0.5 object-cover"
            />
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-secondary rounded-full border-2 border-background flex items-center justify-center">
              <span className="text-[8px] text-white font-bold block translate-y-[-0.5px]">A1</span>
            </div>
          </div>
        </button>
      </div>
    </header>
  );
};

export default Navbar;