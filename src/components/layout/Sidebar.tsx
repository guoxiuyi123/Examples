import { BookOpen, Compass, LayoutDashboard, MessageSquare, User } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navItems = [
  { path: "/dashboard", label: "仪表盘", icon: LayoutDashboard },
  { path: "/courses", label: "课程", icon: Compass },
  { path: "/study", label: "学习", icon: BookOpen },
  { path: "/community", label: "社区", icon: MessageSquare },
  { path: "/profile", label: "我的", icon: User },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <div className="w-64 h-full glass-panel border-r border-white/5 flex flex-col pt-8">
      <div className="px-6 mb-10">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center text-white font-bold text-xl shadow-[0_0_15px_rgba(139,92,246,0.5)]">
            L
          </div>
          <span className="font-bold text-xl tracking-wide text-gradient">LinguaNova</span>
        </Link>
      </div>

      <nav className="flex-1 px-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname.startsWith(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 relative group overflow-hidden",
                isActive
                  ? "text-white font-medium"
                  : "text-muted-foreground hover:text-white"
              )}
            >
              {isActive && (
                <div className="absolute inset-0 bg-primary/10 border border-primary/20 rounded-xl" />
              )}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary rounded-r-full shadow-[0_0_10px_rgba(139,92,246,0.8)]" />
              )}
              
              <div className={cn(
                "relative z-10 transition-transform duration-300 group-hover:scale-110",
                isActive ? "text-primary" : "text-muted-foreground group-hover:text-primary/70"
              )}>
                <Icon size={20} />
              </div>
              <span className="relative z-10">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-white/5">
        <div className="glass-panel p-4 rounded-2xl bg-gradient-to-b from-primary/10 to-transparent border-primary/20">
          <h4 className="text-sm font-semibold mb-2">解锁高级功能</h4>
          <p className="text-xs text-muted-foreground mb-3">
            获取所有语种的无限访问权限及 AI 对话练习。
          </p>
          <button className="w-full py-2 text-xs font-medium rounded-lg bg-primary hover:bg-primary-hover text-white transition-colors shadow-[0_0_15px_rgba(139,92,246,0.3)]">
            升级 Pro
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;