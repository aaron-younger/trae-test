import { Course, VocabularyWord, Achievement, CommunityPost } from '../types';

// 使用内联 SVG 作为课程图片
const courseImages: Record<string, string> = {
  english: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%233b82f6" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="48" fill="white"%3E🇺🇸 English%3C/text%3E%3C/svg%3E',
  japanese: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%23ef4444" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="48" fill="white"%3E🇯🇵 日本語%3C/text%3E%3C/svg%3E',
  korean: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%2310b981" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="48" fill="white"%3E🇰🇷 한국어%3C/text%3E%3C/svg%3E',
};

export const mockCourses: Course[] = [
  {
    id: '1',
    title: '英语入门',
    description: '从零开始学习英语基础',
    language: 'english',
    level: 'beginner',
    imageUrl: courseImages.english,
    lessons: 24,
    duration: '12小时',
    students: 15000,
  },
  {
    id: '2',
    title: '日语基础',
    description: '学习日语的五十音图和基础语法',
    language: 'japanese',
    level: 'beginner',
    imageUrl: courseImages.japanese,
    lessons: 30,
    duration: '15小时',
    students: 12000,
  },
  {
    id: '3',
    title: '韩语入门',
    description: '学习韩语字母和日常用语',
    language: 'korean',
    level: 'beginner',
    imageUrl: courseImages.korean,
    lessons: 20,
    duration: '10小时',
    students: 8000,
  },
  {
    id: '4',
    title: '英语进阶',
    description: '提高英语听说读写能力',
    language: 'english',
    level: 'intermediate',
    imageUrl: courseImages.english,
    lessons: 32,
    duration: '16小时',
    students: 9000,
  },
];

export const mockVocabulary: VocabularyWord[] = [
  {
    id: '1',
    word: 'Hello',
    translation: '你好',
    pronunciation: 'heh-LOH',
    example: 'Hello, how are you?',
    difficulty: 'easy',
  },
  {
    id: '2',
    word: 'Thank you',
    translation: '谢谢',
    pronunciation: 'THANK yoo',
    example: 'Thank you very much.',
    difficulty: 'easy',
  },
  {
    id: '3',
    word: 'Goodbye',
    translation: '再见',
    pronunciation: 'good-BYE',
    example: 'Goodbye, see you tomorrow.',
    difficulty: 'easy',
  },
  {
    id: '4',
    word: 'Please',
    translation: '请',
    pronunciation: 'PLEEZ',
    example: 'Please, come in.',
    difficulty: 'easy',
  },
  {
    id: '5',
    word: 'Sorry',
    translation: '对不起',
    pronunciation: 'SAH-ree',
    example: 'I am sorry.',
    difficulty: 'easy',
  },
];

export const mockAchievements: Achievement[] = [
  {
    id: '1',
    name: '初学者',
    description: '完成第一次练习',
    icon: '🎯',
    earned: true,
    date: '2024-01-15',
  },
  {
    id: '2',
    name: '坚持一周',
    description: '连续7天学习',
    icon: '🔥',
    earned: true,
    date: '2024-01-22',
  },
  {
    id: '3',
    name: '词汇达人',
    description: '学习100个单词',
    icon: '📚',
    earned: true,
    date: '2024-01-28',
  },
  {
    id: '4',
    name: '听力大师',
    description: '完成20个听力练习',
    icon: '🎧',
    earned: false,
  },
  {
    id: '5',
    name: '语法专家',
    description: '完成50个语法练习',
    icon: '✍️',
    earned: false,
  },
  {
    id: '6',
    name: '口语高手',
    description: '完成30个口语练习',
    icon: '🎤',
    earned: false,
  },
];

export const mockCommunityPosts: CommunityPost[] = [
  {
    id: '1',
    userId: 'user1',
    userName: '李明',
    content: '刚刚完成了英语入门课程，感觉进步很大！分享一下我的学习心得...',
    language: 'english',
    likes: 42,
    comments: 8,
    timestamp: '2小时前',
  },
  {
    id: '2',
    userId: 'user2',
    userName: '樱子',
    content: '日语五十音图好难记啊，大家有什么好方法吗？',
    language: 'japanese',
    likes: 28,
    comments: 15,
    timestamp: '5小时前',
  },
  {
    id: '3',
    userId: 'user3',
    userName: '哲秀',
    content: '韩语发音练习了一个月，终于找到感觉了！加油！',
    language: 'korean',
    likes: 35,
    comments: 12,
    timestamp: '1天前',
  },
];
