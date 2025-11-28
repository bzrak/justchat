import type { ChannelJoinMessage } from '../../types/messages';

interface ChannelJoinMessageProps {
  message: ChannelJoinMessage;
}

export function ChannelJoinMessage({ message }: ChannelJoinMessageProps) {
  const { payload, timestamp } = message;

  return (
    <div className="flex justify-center my-3">
      <div className="bg-gray-200 text-gray-700 px-4 py-2 rounded-full text-sm">
        <span className="font-semibold">{payload.username}</span>
        {' joined the channel'}
        <span className="text-xs text-gray-500 ml-2">
          {new Date(timestamp).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
}
