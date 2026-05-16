import { useState } from 'react';
import { Heart, MessageCircle, Share2, Users, Plus, Search, MessageSquare } from 'lucide-react';
import { mockCommunityPosts } from '../data/mockData';

const Community = () => {
  const [activeTab, setActiveTab] = useState<'all' | 'english' | 'japanese' | 'korean'>('all');
  const [likedPosts, setLikedPosts] = useState<Set<string>>(new Set());

  const filteredPosts = activeTab === 'all'
    ? mockCommunityPosts
    : mockCommunityPosts.filter(post => post.language === activeTab);

  const toggleLike = (postId: string) => {
    setLikedPosts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(postId)) {
        newSet.delete(postId);
      } else {
        newSet.add(postId);
      }
      return newSet;
    });
  };

  const studyGroups = [
    { id: 1, name: '英语日常交流', members: 128, language: 'english' },
    { id: 2, name: '日语N2备考', members: 89, language: 'japanese' },
    { id: 3, name: '韩语入门学习', members: 67, language: 'korean' },
    { id: 4, name: '英语商务写作', members: 54, language: 'english' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">学习社区</h1>
          <p className="text-gray-600">与其他学习者交流和分享</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-3xl p-6 shadow-lg">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                  我
                </div>
                <input
                  type="text"
                  placeholder="分享你的学习心得..."
                  className="flex-1 px-4 py-3 bg-gray-100 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                />
                <button className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 transition-colors">
                  <Plus className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="flex gap-2 overflow-x-auto pb-2">
              {[
                { key: 'all', label: '全部' },
                { key: 'english', label: '英语' },
                { key: 'japanese', label: '日语' },
                { key: 'korean', label: '韩语' },
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`px-6 py-2 rounded-full font-medium whitespace-nowrap transition-all ${
                    activeTab === tab.key
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {filteredPosts.map(post => {
              const isLiked = likedPosts.has(post.id);
              return (
                <div key={post.id} className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      {post.userAvatar ? (
                        <img
                          src={post.userAvatar}
                          alt={post.userName}
                          className="w-12 h-12 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                          <Users className="w-6 h-6 text-gray-400" />
                        </div>
                      )}
                      <div>
                        <div className="font-semibold text-gray-900">{post.userName}</div>
                        <div className="text-sm text-gray-500">{post.timestamp}</div>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      post.language === 'english'
                        ? 'bg-blue-100 text-blue-800'
                        : post.language === 'japanese'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {post.language === 'english' ? '英语' : post.language === 'japanese' ? '日语' : '韩语'}
                    </span>
                  </div>
                  <p className="text-gray-700 mb-4">{post.content}</p>
                  <div className="flex items-center gap-6">
                    <button
                      onClick={() => toggleLike(post.id)}
                      className={`flex items-center gap-2 transition-colors ${
                        isLiked ? 'text-red-500' : 'text-gray-500 hover:text-red-500'
                      }`}
                    >
                      <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
                      <span>{isLiked ? post.likes + 1 : post.likes}</span>
                    </button>
                    <button className="flex items-center gap-2 text-gray-500 hover:text-blue-500 transition-colors">
                      <MessageCircle className="w-5 h-5" />
                      <span>{post.comments}</span>
                    </button>
                    <button className="flex items-center gap-2 text-gray-500 hover:text-green-500 transition-colors">
                      <Share2 className="w-5 h-5" />
                      <span>分享</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-3xl p-6 shadow-lg">
              <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Users className="w-5 h-5" />
                学习小组
              </h3>
              <div className="space-y-4">
                {studyGroups.map(group => (
                  <div key={group.id} className="p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-gray-900">{group.name}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        group.language === 'english'
                          ? 'bg-blue-100 text-blue-800'
                          : group.language === 'japanese'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {group.language === 'english' ? '英语' : group.language === 'japanese' ? '日语' : '韩语'}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-gray-500">
                      <Users className="w-4 h-4" />
                      <span>{group.members} 成员</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-3xl p-6 shadow-lg">
              <h3 className="font-bold text-gray-900 mb-4">活跃用户</h3>
              <div className="space-y-4">
                {[
                  { name: '张小明', initial: '张', streak: 8 },
                  { name: '李华', initial: '李', streak: 9 },
                  { name: '王芳', initial: '王', streak: 10 },
                  { name: '刘伟', initial: '刘', streak: 11 },
                ].map((user, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
                      {user.initial}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{user.name}</div>
                      <div className="text-sm text-gray-500">连续学习 {user.streak} 天</div>
                    </div>
                    <button className="text-indigo-600 font-medium text-sm hover:text-indigo-700">
                      关注
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Community;
