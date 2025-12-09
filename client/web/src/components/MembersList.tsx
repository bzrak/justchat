interface Member {
  username: string
  isOnline: boolean
}

interface MembersListProps {
  members: Member[]
  currentChannelId: number | null
}

export function MembersList({ members, currentChannelId }: MembersListProps) {
  console.log('[MembersList] Rendering with:', {
    currentChannelId,
    memberCount: members.length,
    members: members.map(m => m.username)
  })

  if (currentChannelId === null) {
    return (
      <div className="w-64 bg-gray-800 text-white flex flex-col h-screen">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
            Members
          </h2>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <p className="text-sm text-gray-500 italic text-center px-4">
            Select a channel to see members
          </p>
        </div>
      </div>
    )
  }

  // Sort members: online first, then alphabetically
  const sortedMembers = [...members].sort((a, b) => {
    if (a.isOnline !== b.isOnline) {
      return a.isOnline ? -1 : 1
    }
    return a.username.localeCompare(b.username)
  })

  const onlineCount = members.filter(m => m.isOnline).length
  const offlineCount = members.length - onlineCount

  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-1">
          Members
        </h2>
        <p className="text-xs text-gray-500">
          {members.length} {members.length === 1 ? 'member' : 'members'}
        </p>
      </div>

      {/* Members List */}
      <div className="flex-1 overflow-y-auto">
        {members.length === 0 ? (
          <div className="p-4">
            <p className="text-sm text-gray-500 italic text-center">
              No members in this channel
            </p>
          </div>
        ) : (
          <div className="p-3 space-y-4">
            {/* Online Members */}
            {onlineCount > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-2">
                  Online — {onlineCount}
                </h3>
                <div className="space-y-1">
                  {sortedMembers
                    .filter(member => member.isOnline)
                    .map((member) => (
                      <MemberItem key={member.username} member={member} />
                    ))}
                </div>
              </div>
            )}

            {/* Offline Members */}
            {offlineCount > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-2">
                  Offline — {offlineCount}
                </h3>
                <div className="space-y-1">
                  {sortedMembers
                    .filter(member => !member.isOnline)
                    .map((member) => (
                      <MemberItem key={member.username} member={member} />
                    ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function MemberItem({ member }: { member: Member }) {
  // Generate a consistent color based on username
  const getAvatarColor = (username: string) => {
    const colors = [
      'bg-red-500',
      'bg-blue-500',
      'bg-green-500',
      'bg-yellow-500',
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
      'bg-teal-500',
      'bg-orange-500',
      'bg-cyan-500',
    ]
    const hash = username.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    return colors[hash % colors.length]
  }

  const avatarColor = getAvatarColor(member.username)

  return (
    <div className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-gray-700 transition-colors cursor-pointer group">
      {/* Avatar */}
      <div className="relative">
        <div
          className={`flex items-center justify-center w-8 h-8 ${avatarColor} rounded-full font-semibold text-sm shadow`}
        >
          {member.username[0].toUpperCase()}
        </div>
        {/* Status indicator */}
        <div
          className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-gray-800 ${
            member.isOnline ? 'bg-green-500' : 'bg-gray-500'
          }`}
        />
      </div>

      {/* Username */}
      <div className="flex-1 min-w-0">
        <p className={`text-sm truncate ${member.isOnline ? 'text-white' : 'text-gray-400'}`}>
          {member.username}
        </p>
      </div>
    </div>
  )
}
