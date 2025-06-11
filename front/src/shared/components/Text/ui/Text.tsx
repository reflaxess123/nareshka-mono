import { clsx } from 'clsx';
import { TextAlign, TextSize, TextWeight } from '../model/types';
import styles from './Text.module.scss';

interface TextProps {
  text: string;
  className?: string;
  size?: TextSize;
  weight?: TextWeight;
  align?: TextAlign;
}

export const Text = ({
  text,
  className,
  size = TextSize.MD,
  weight = TextWeight.NORMAL,
  align = TextAlign.LEFT,
}: TextProps) => {
  return (
    <div
      className={clsx(
        styles.text,
        className,
        styles[size],
        styles[weight],
        styles[align]
      )}
    >
      {text}
    </div>
  );
};
