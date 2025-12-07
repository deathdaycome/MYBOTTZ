import { motion } from 'motion/react';

interface FadeTextProps {
  text: string;
  className?: string;
  delay?: number;
  duration?: number;
  direction?: 'up' | 'down' | 'none';
}

const FadeText: React.FC<FadeTextProps> = ({
  text,
  className = '',
  delay = 0.05,
  duration = 0.5,
  direction = 'up'
}) => {
  const words = text.split(' ');

  const getInitialY = () => {
    if (direction === 'up') return 20;
    if (direction === 'down') return -20;
    return 0;
  };

  return (
    <p className={className} style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25em' }}>
      {words.map((word, index) => (
        <motion.span
          key={index}
          initial={{
            opacity: 0,
            y: getInitialY()
          }}
          animate={{
            opacity: 1,
            y: 0
          }}
          transition={{
            duration: duration,
            delay: index * delay,
            ease: [0.25, 0.4, 0.25, 1]
          }}
          style={{
            display: 'inline-block',
            whiteSpace: 'pre'
          }}
        >
          {word}
        </motion.span>
      ))}
    </p>
  );
};

export default FadeText;
