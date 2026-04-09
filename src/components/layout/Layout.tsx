import { Outlet, useLocation, Link } from "react-router-dom";
import { BookOpen, Compass, LayoutDashboard, MessageSquare, User } from "lucide-react";
import Navbar from "./Navbar";
import Sidebar, { cn } from "./Sidebar";

const navItems = [
  { path: "/dashboard", label: "仪表盘", icon: LayoutDashboard },
  { path: "/courses", label: "课程", icon: Compass },
  { path: "/study", label: "学习", icon: BookOpen },
  { path: "/community", label: "社区", icon: MessageSquare },
  { path: "/profile", label: "我的", icon: User },
];

const Layout = () => {
  const location = useLocation();

  return (
    <div className="h-screen w-full flex flex-col md:flex-row bg-background text-foreground overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex w-64 flex-shrink-0 z-20">
        <Sidebar />
      </div>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 h-full relative">
        <Navbar />
        
        {/* Content scroll area */}
        <div className="flex-1 overflow-y-auto pb-20 md:pb-0 custom-scrollbar">
          <div className="p-4 md:p-8 max-w-7xl mx-auto w-full">
            <Outlet />
          </div>
        </div>
      </main>
      
      {/* Mobile Bottom Navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 glass-panel border-t border-white/10 z-50 pb-safe">
         <nav className="flex items-center justify-around px-2 py-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);

            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex flex-col items-center gap-1 p-2 min-w-[64px] transition-all relative",
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground hover:text-white"
                )}
              >
                {isActive && (
                  <span className="absolute -top-3 w-8 h-1 bg-primary rounded-b-full shadow-[0_0_10px_rgba(139,92,246,0.8)]" />
                )}
                <Icon size={20} className={cn("transition-transform", isActive ? "scale-110" : "")} />
                <span className="text-[10px] font-medium">{item.label}</span>
              </Link>
            );
          })}
         </nav>
      </div>
    </div>
  );
};

export default Layout;