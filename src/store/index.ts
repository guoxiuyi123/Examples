import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  avatar: string;
  level: string;
  xp: number;
  streak: number;
}

interface CourseProgress {
  courseId: string;
  completedModules: string[];
  lastAccessed: number;
}

interface AppState {
  user: User | null;
  coursesProgress: Record<string, CourseProgress>;
  isDarkMode: boolean;
  login: (userData: User) => void;
  logout: () => void;
  updateXP: (amount: number) => void;
  completeModule: (courseId: string, moduleId: string) => void;
  toggleDarkMode: () => void;
}

const MOCK_USER: User = {
  id: 'u1',
  name: 'Alex Chen',
  avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex&backgroundColor=8b5cf6',
  level: 'Lv. 15 初学者',
  xp: 2120,
  streak: 12,
};

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      user: MOCK_USER,
      coursesProgress: {
        'c1': {
          courseId: 'c1',
          completedModules: ['m1', 'm2', 'm3'],
          lastAccessed: Date.now(),
        }
      },
      isDarkMode: true,
      
      login: (userData) => set({ user: userData }),
      
      logout: () => set({ user: null }),
      
      updateXP: (amount) => set((state) => ({
        user: state.user ? { ...state.user, xp: state.user.xp + amount } : null
      })),
      
      completeModule: (courseId, moduleId) => set((state) => {
        const currentProgress = state.coursesProgress[courseId] || {
          courseId,
          completedModules: [],
          lastAccessed: Date.now(),
        };
        
        if (!currentProgress.completedModules.includes(moduleId)) {
          return {
            coursesProgress: {
              ...state.coursesProgress,
              [courseId]: {
                ...currentProgress,
                completedModules: [...currentProgress.completedModules, moduleId],
                lastAccessed: Date.now(),
              }
            }
          };
        }
        return state;
      }),
      
      toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
    }),
    {
      name: 'lingua-nova-storage',
    }
  )
);
