import { motion } from 'framer-motion';

interface ProgressBarProps {
  progress: number; // 0-100
  timeSpentSeconds: number;
  className?: string;
}

export const ProgressBar = ({ progress, timeSpentSeconds, className = '' }: ProgressBarProps) => {
  const hours = Math.floor(timeSpentSeconds / 3600);
  const minutes = Math.floor((timeSpentSeconds % 3600) / 60);
  const timeFormatted = hours > 0 ? `${hours}ч ${minutes}м` : `${minutes}м`;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex justify-between items-center text-sm">
        <span className="font-medium text-gray-700">Прогресс выполнения</span>
        <div className="flex items-center gap-3">
          <span className="text-gray-600">⏱ {timeFormatted}</span>
          <span className="font-semibold text-primary-600">{progress}%</span>
        </div>
      </div>
      
      <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
        <motion.div
          className="absolute top-0 left-0 h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
      
      {/* Визуальный индикатор прогресса */}
      <div className="flex text-xs text-gray-500">
        <span className={progress >= 25 ? 'text-primary-600 font-medium' : ''}>0%</span>
        <span className="flex-1 text-center">
          <span className={progress >= 50 ? 'text-primary-600 font-medium' : ''}>50%</span>
        </span>
        <span className={progress === 100 ? 'text-green-600 font-medium' : ''}>100%</span>
      </div>
    </div>
  );
};
