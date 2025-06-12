declare module 'lucide-react' {
  import { FC, SVGProps } from 'react';

  export interface LucideProps extends SVGProps<SVGSVGElement> {
    size?: number | string;
    absoluteStrokeWidth?: boolean;
  }

  export type LucideIcon = FC<LucideProps>;

  export const BrainCircuit: LucideIcon;
  export const Code: LucideIcon;
  export const Database: LucideIcon;
  export const BarChart3: LucideIcon;
  export const Eye: LucideIcon;
  export const Scale: LucideIcon;
  export const DollarSign: LucideIcon;
  export const MessageCircle: LucideIcon;
} 