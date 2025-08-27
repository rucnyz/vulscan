import React, { Suspense } from "react";
const ReactMarkdown = React.lazy(() => import("react-markdown"));
const SyntaxHighlighter = React.lazy(() =>
  import("react-syntax-highlighter").then((module) => ({
    default: module.Prism,
  }))
);
import { oneLight } from "react-syntax-highlighter/dist/cjs/styles/prism";

interface MarkdownRendererProps {
  content: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ReactMarkdown
        components={{
          // For inline code, just return a standard code element
          code(props) {
            const { children, ...rest } = props;
            return (
              <code
                {...rest}
                style={{ fontSize: "0.8em" }}
                className="bg-gray-100 rounded-md px-1 py-0.5"
              >
                {children}
              </code>
            );
          },

          // For pre elements, check if child is a code element and transform to SyntaxHighlighter
          pre(props) {
            const { children, ...rest } = props;

            // Get the first child (which should be our code element)
            const child = React.Children.toArray(children)[0];

            // Check if it's a React element and if its type is a function named "code"
            if (
              React.isValidElement(child) &&
              typeof child.type === "function" &&
              child.type.name === "code"
            ) {
              // @ts-ignore
              // Extract the actual code content from the child's props
              const codeContent = child.props.children || "";

              // Try to get language from the node properties if available
              const language =
                // @ts-ignore
                child.props.node?.properties?.className?.[0]?.split("-")[1] ||
                "cpp";

              return (
                // @ts-ignore
                <SyntaxHighlighter
                  {...rest}
                  PreTag="div"
                  children={String(codeContent).replace(/\n$/, "")}
                  language={language}
                  lineProps={{ style: { whiteSpace: "pre-wrap" } }}
                  style={oneLight}
                  wrapLines={true}
                  showLineNumbers={true}
                  customStyle={{ fontSize: "0.8rem" }}
                />
              ); // @ts-ignore
            }

            // If not a code element, return pre as is
            return <pre {...rest}>{children}</pre>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </Suspense>
  );
};

export default MarkdownRenderer;
