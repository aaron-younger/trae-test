import { useState } from 'react';
import { User, Settings, Bell, BookOpen, Award, ChevronRight, LogOut } from 'lucide-react';
import { useAppStore } from '../store';

const Profile = () => {
  const { user, logout } = useAppStore();
  const [activeTab, setActiveTab] = useState<'info' | 'settings'>('info');

  const menuItems = [
    { icon: User, label: '个人信息', tab: 'info' },
    { icon: Settings, label: '账号设置', tab: 'settings' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-3xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-indigo-500 to-purple-500 p-8 text-white">
            <div className="flex items-center gap-6">
              {user?.avatarUrl ? (
                <img
                  src={user.avatarUrl}
                  alt={user.name}
                  className="w-24 h-24 rounded-full border-4 border-white/30 object-cover"
                />
              ) : (
                <div className="w-24 h-24 rounded-full border-4 border-white/30 bg-white/20 flex items-center justify-center">
                  <User className="w-12 h-12 text-white" />
                </div>
              )}
              <div>
                <h1 className="text-2xl font-bold">{user?.name || '学习者'}</h1>
                <div className="flex items-center gap-2 text-white/80">
                  <span>Lv.{user?.level || 1}</span>
                  <span>·</span>
                  <span>{user?.totalPoints || 0} 积分</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex border-b">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.tab}
                  onClick={() => setActiveTab(item.tab as any)}
                  className={`flex-1 py-4 px-6 flex items-center justify-center gap-2 font-medium transition-colors ${
                    activeTab === item.tab
                      ? 'text-indigo-600 border-b-2 border-indigo-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {item.label}
                </button>
              );
            })}
          </div>

          <div className="p-8">
            {activeTab === 'info' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-bold text-gray-900 mb-4">基本信息</h2>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-3 border-b border-gray-100">
                      <span className="text-gray-600">用户名</span>
                      <span className="font-medium text-gray-900">{user?.name || '未设置'}</span>
                    </div>
                    <div className="flex items-center justify-between py-3 border-b border-gray-100">
                      <span className="text-gray-600">邮箱</span>
                      <span className="font-medium text-gray-900">{user?.email || '未设置'}</span>
                    </div>
                    <div className="flex items-center justify-between py-3 border-b border-gray-100">
                      <span className="text-gray-600">学习天数</span>
                      <span className="font-medium text-gray-900">15 天</span>
                    </div>
                    <div className="flex items-center justify-between py-3 border-b border-gray-100">
                      <span className="text-gray-600">学习语言</span>
                      <span className="font-medium text-gray-900">英语, 日语</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h2 className="text-lg font-bold text-gray-900 mb-4">学习数据</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 rounded-2xl p-4">
                      <div className="text-2xl font-bold text-blue-600">450</div>
                      <div className="text-sm text-gray-600">已学单词</div>
                    </div>
                    <div className="bg-green-50 rounded-2xl p-4">
                      <div className="text-2xl font-bold text-green-600">8</div>
                      <div className="text-sm text-gray-600">完成课程</div>
                    </div>
                    <div className="bg-purple-50 rounded-2xl p-4">
                      <div className="text-2xl font-bold text-purple-600">32</div>
                      <div className="text-sm text-gray-600">学习小时</div>
                    </div>
                    <div className="bg-orange-50 rounded-2xl p-4">
                      <div className="text-2xl font-bold text-orange-600">15</div>
                      <div className="text-sm text-gray-600">连续学习</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-bold text-gray-900 mb-4">账号设置</h2>
                  <div className="space-y-4">
                    <button className="w-full flex items-center justify-between py-3 px-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                      <span className="flex items-center gap-3">
                        <Bell className="w-5 h-5 text-gray-500" />
                        <span className="text-gray-700">通知设置</span>
                      </span>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </button>
                    <button className="w-full flex items-center justify-between py-3 px-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                      <span className="flex items-center gap-3">
                        <BookOpen className="w-5 h-5 text-gray-500" />
                        <span className="text-gray-700">学习偏好</span>
                      </span>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </button>
                    <button className="w-full flex items-center justify-between py-3 px-4 bg-gray-50 rounded-xl hover:bg-gray-100">
                      <span className="flex items-center gap-3">
                        <User className="w-5 h-5 text-gray-500" />
                        <span className="text-gray-700">隐私设置</span>
                      </span>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </button>
                    <button className="w-full flex items-center justify-between py-3 px-4 bg-gray-50 rounded-xl hover:bg-gray-100">
                      <span className="flex items-center gap-3">
                        <Settings className="w-5 h-5 text-gray-500" />
                        <span className="text-gray-700">关于我们</span>
                      </span>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </button>
                  </div>
                </div>

                <div>
                  <button
                    onClick={logout}
                    className="w-full flex items-center justify-center gap-2 py-4 px-6 bg-red-50 text-red-600 rounded-xl hover:bg-red-100 transition-colors font-medium"
                  >
                    <LogOut className="w-5 h-5" />
                    退出登录
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
