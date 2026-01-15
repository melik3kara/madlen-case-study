declare module 'react-syntax-highlighter' {
  import { ComponentType, ReactNode } from 'react';
  
  export interface SyntaxHighlighterProps {
    children: string | string[];
    style?: Record<string, React.CSSProperties>;
    language?: string;
    showLineNumbers?: boolean;
    wrapLines?: boolean;
    wrapLongLines?: boolean;
    lineProps?: object | ((lineNumber: number) => object);
    customStyle?: React.CSSProperties;
    codeTagProps?: object;
    useInlineStyles?: boolean;
    PreTag?: string | ComponentType<any>;
    CodeTag?: string | ComponentType<any>;
    className?: string;
  }
  
  export const Prism: ComponentType<SyntaxHighlighterProps>;
  export const Light: ComponentType<SyntaxHighlighterProps>;
  export default ComponentType<SyntaxHighlighterProps>;
}

declare module 'react-syntax-highlighter/dist/esm/styles/prism' {
  const oneDark: Record<string, React.CSSProperties>;
  const oneLight: Record<string, React.CSSProperties>;
  const vscDarkPlus: Record<string, React.CSSProperties>;
  const atomDark: Record<string, React.CSSProperties>;
  const coldarkDark: Record<string, React.CSSProperties>;
  const coldarkCold: Record<string, React.CSSProperties>;
  const materialDark: Record<string, React.CSSProperties>;
  const materialLight: Record<string, React.CSSProperties>;
  const nord: Record<string, React.CSSProperties>;
  const tomorrow: Record<string, React.CSSProperties>;
  
  export {
    oneDark,
    oneLight,
    vscDarkPlus,
    atomDark,
    coldarkDark,
    coldarkCold,
    materialDark,
    materialLight,
    nord,
    tomorrow
  };
}
