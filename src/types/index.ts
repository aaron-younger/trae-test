export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  level: number;
  totalPoints: number;
}

export interface Course {
  id: string;
  title: string;
  description: string;
  language: 'english' | 'japanese' | 'korean';
  level: 'beginner' | 'intermediate' | 'advanced';
  imageUrl: string;
  lessons: number;
  duration: string;
  students: number;
}

export interface Lesson {
  id: string;
  courseId: string;
  title: string;
  description: string;
  duration: number;
  completed: boolean;
}

export interface VocabularyWord {
  id: string;
  word: string;
  translation: string;
  pronunciation: string;
  example: string;
  imageUrl?: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  earned: boolean;
  date?: string;
}

export interface CommunityPost {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  content: string;
  language: string;
  likes: number;
  comments: number;
  timestamp: string;
}
