import { Trophy, BookOpen, TrendingUp, Calendar, Target, Award } from 'lucide-react';
import { mockAchievements } from '../data/mockData';

const Progress = () => {
  const weeklyData = [
    { day: '周一', minutes: 45 },
    { day: '周二', minutes: 60 },
    { day: '周三', minutes: 30 },
    { day: '周四', minutes: 75 },
    { day: '周五', minutes: 50 },
    { day: '周六', minutes: 90 },
    { day: '周日', minutes: 40 },
  ];

  const stats = [
    { label: '连续学习', value: '15天', icon: Calendar, color: 'blue' },
    { label: '学习时长', value: '32小时', icon: TrendingUp, color: 'green' },
    { label: '已学单词', value: '450个', icon: BookOpen, color: 'purple' },
    { label: '完成课程', value: '8门', icon: Target, color: 'orange' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">学习进度</h1>
          <p className="text-gray-600">查看你的学习数据和成就</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div key={index} className="bg-white rounded-3xl p-6 shadow-lg hover:shadow-xl transition-all">
                <div className={`w-12 h-12 bg-${stat.color}-100 rounded-xl flex items-center justify-center mb-4`}>
                  <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
                <div className="text-gray-500">{stat.label}</div>
              </div>
            );
          })}
        </div>

        <div className="bg-white rounded-3xl p-6 shadow-lg mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            本周学习统计
          </h2>
          <div className="h-48 flex items-end justify-between gap-4">
            {weeklyData.map((item, index) => {
              const height = Math.max((item.minutes / 90) * 100, 10);
              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div className="w-full bg-gray-100 rounded-t-xl relative" style={{ height: '160px' }}>
                    <div
                      className="absolute bottom-0 w-full bg-gradient-to-t from-indigo-500 to-purple-500 rounded-t-xl transition-all hover:from-indigo-600 hover:to-purple-600"
                      style={{ height: `${height}%` }}
                    />
                  </div>
                  <div className="text-sm text-gray-600 mt-2">{item.day}</div>
                  <div className="text-xs text-gray-400">{item.minutes}分</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 shadow-lg mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Trophy className="w-5 h-5" />
              成就系统
            </h2>
            <span className="text-gray-500">
              {mockAchievements.filter(a => a.earned).length} / {mockAchievements.length} 已获得
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mockAchievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`p-4 rounded-2xl border-2 transition-all ${
                  achievement.earned
                    ? 'bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200'
                    : 'bg-gray-50 border-gray-200 opacity-50'
                }`}
              >
                <div className="flex items-center gap-4">
                  <div className="text-4xl">{achievement.icon}</div>
                  <div>
                    <h3 className="font-bold text-gray-900">{achievement.name}</h3>
                    <p className="text-sm text-gray-600">{achievement.description}</p>
                    {achievement.earned && achievement.date && (
                      <p className="text-xs text-gray-400 mt-1">获得于 {achievement.date}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 shadow-lg">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Award className="w-5 h-5" />
            语言水平
          </h2>
          <div className="space-y-6">
            {[
              { language: '英语', level: '中级', progress: 65 },
              { language: '日语', level: '初级', progress: 35 },
              { language: '韩语', level: '入门', progress: 15 },
            ].map((item, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="font-semibold text-gray-900">{item.language}</span>
                    <span className="ml-2 text-sm text-gray-500">({item.level})</span>
                  </div>
                  <span className="text-sm font-medium text-indigo-600">{item.progress}%</span>
                </div>
                <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Progress;
