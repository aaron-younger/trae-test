import { Link } from 'react-router-dom';
import { BookOpen, Play, Volume2, MessageSquare, Trophy, TrendingUp } from 'lucide-react';
import { useAppStore } from '../store';
import { mockCourses } from '../data/mockData';

const Dashboard = () => {
  const { user, todayMinutes, streak, wordsLearned, coursesCompleted } = useAppStore();

  const quickActions = [
    { icon: BookOpen, label: '单词学习', path: '/vocabulary', color: 'blue' },
    { icon: MessageSquare, label: '语法练习', path: '/grammar', color: 'green' },
    { icon: Volume2, label: '听力训练', path: '/listening', color: 'purple' },
    { icon: Play, label: '口语跟读', path: '/speaking', color: 'orange' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            欢迎回来，{user?.name || '学习者'}！
          </h1>
          <p className="text-gray-600">今天继续你的语言学习之旅吧</p>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-3xl p-6 shadow-lg hover:shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-2xl">🔥</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-1">{streak}天</h3>
            <p className="text-gray-500 text-sm">连续学习</p>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-lg hover:shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-2xl">📚</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-1">{wordsLearned}</h3>
            <p className="text-gray-500 text-sm">单词学习</p>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-lg hover:shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <Trophy className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-2xl">🏆</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-1">{coursesCompleted}</h3>
            <p className="text-gray-500 text-sm">课程完成</p>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-lg hover:shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-orange-600" />
              </div>
              <span className="text-2xl">⏰</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-1">{todayMinutes}分钟</h3>
            <p className="text-gray-500 text-sm">今日学习</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">快速开始</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <Link
                key={index}
                to={action.path}
                className="bg-white rounded-2xl p-6 text-center shadow-lg hover:shadow-xl hover:scale-105 transition-all group"
              >
                <div
                  className={`w-16 h-16 mx-auto mb-3 rounded-2xl flex items-center justify-center bg-${action.color}-100 group-hover:bg-${action.color}-200 transition-colors`}
                >
                  <action.icon className={`w-8 h-8 text-${action.color}-600`} />
                </div>
                <span className="font-semibold text-gray-800">{action.label}</span>
              </Link>
            ))}
          </div>
        </div>

        {/* Recommended Courses */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">推荐课程</h2>
            <Link to="/courses" className="text-indigo-600 hover:text-indigo-700 font-medium">
              查看全部 →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {mockCourses.map((course) => (
              <Link
                key={course.id}
                to={`/courses/${course.id}`}
                className="bg-white rounded-3xl overflow-hidden shadow-lg hover:shadow-xl hover:scale-105 transition-all group"
              >
                <div className="relative h-48">
                  <img
                    src={course.imageUrl}
                    alt={course.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                  />
                  <div className="absolute top-4 right-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        course.language === 'english'
                          ? 'bg-blue-100 text-blue-800'
                          : course.language === 'japanese'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {course.language === 'english' ? '英语' : course.language === 'japanese' ? '日语' : '韩语'}
                    </span>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="font-bold text-gray-900 text-lg mb-2">{course.title}</h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{course.description}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{course.lessons}节课</span>
                    <span>{course.duration}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
