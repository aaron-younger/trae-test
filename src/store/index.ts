import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  level: number;
  totalPoints: number;
}

interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  selectedLanguage: string;
  selectedLevel: string;
  todayMinutes: number;
  streak: number;
  totalDays: number;
  wordsLearned: number;
  coursesCompleted: number;
  
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, name: string) => Promise<boolean>;
  logout: () => void;
  setSelectedLanguage: (language: string) => void;
  setSelectedLevel: (level: string) => void;
  updateProgress: (minutes: number, words: number) => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  isAuthenticated: false,
  selectedLanguage: 'english',
  selectedLevel: 'beginner',
  todayMinutes: 45,
  streak: 7,
  totalDays: 23,
  wordsLearned: 156,
  coursesCompleted: 2,

  login: async (email: string, password: string) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    set({
      user: {
        id: 'user1',
        email,
        name: '学习者',
        avatarUrl: 'https://i.pravatar.cc/150?img=12',
        level: 5,
        totalPoints: 2340,
      },
      isAuthenticated: true,
    });
    return true;
  },

  register: async (email: string, password: string, name: string) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    set({
      user: {
        id: 'user1',
        email,
        name,
        avatarUrl: 'https://i.pravatar.cc/150?img=12',
        level: 1,
        totalPoints: 0,
      },
      isAuthenticated: true,
    });
    return true;
  },

  logout: () => {
    set({ user: null, isAuthenticated: false });
  },

  setSelectedLanguage: (language: string) => {
    set({ selectedLanguage: language });
  },

  setSelectedLevel: (level: string) => {
    set({ selectedLevel: level });
  },

  updateProgress: (minutes: number, words: number) => {
    set((state) => ({
      todayMinutes: state.todayMinutes + minutes,
      wordsLearned: state.wordsLearned + words,
    }));
  },
}));
