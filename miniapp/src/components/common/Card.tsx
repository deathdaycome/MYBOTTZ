import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hoverable = false,
  onClick,
}) => {
  const Component = hoverable || onClick ? motion.div : 'div';

  return (
    <Component
      className={`card ${hoverable ? 'card-hover cursor-pointer' : ''} ${className}`}
      onClick={onClick}
      {...(hoverable || onClick
        ? {
            whileHover: { scale: 1.02 },
            whileTap: { scale: 0.98 },
            transition: { duration: 0.2 },
          }
        : {})}
    >
      {children}
    </Component>
  );
};
