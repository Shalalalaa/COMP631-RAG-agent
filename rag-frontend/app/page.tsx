"use client";

import { useState, useRef, useEffect } from "react";
import styled from "styled-components";

// 类型定义
type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  emotions?: string[];
  sciTitles?: string[];
  folkTitles?: string[];
  freudTitles?: string[];
};

// 样式组件
const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  height: 100vh;
  display: flex;
  flex-direction: column;
`;

const ChatHistory = styled.div`
  flex: 1;
  overflow-y: auto;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 1rem;
`;

const MessageBubble = styled.div<{ $isUser: boolean }>`
  display: flex;
  flex-direction: column;
  margin: 0.8rem 0;
  align-items: ${({ $isUser }) => $isUser ? 'flex-end' : 'flex-start'};

  .content {
    max-width: 85%;
    padding: 1rem 1.2rem;
    border-radius: ${({ $isUser }) => 
      $isUser ? '15px 15px 0 15px' : '15px 15px 15px 0'};
    background: ${({ $isUser }) => 
      $isUser ? '#3b82f6' : 'white'};
    color: ${({ $isUser }) => $isUser ? 'white' : '#1f2937'};
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    line-height: 1.6;
  }

  .meta {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 0.5rem;
    display: flex;
    gap: 0.5rem;
  }
`;

const InputArea = styled.div`
  position: relative;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  transition: border-color 0.2s;

  &:focus-within {
    border-color: #3b82f6;
  }

  textarea {
    width: 100%;
    padding: 1rem 4rem 1rem 1rem;
    border: none;
    border-radius: 12px;
    resize: none;
    font-size: 1rem;
    min-height: 100px;

    &:focus {
      outline: none;
    }
  }

  button {
    position: absolute;
    bottom: 1rem;
    right: 1rem;
    padding: 0.5rem 1rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: opacity 0.2s;

    &:disabled {
      background: #9ca3af;
      cursor: not-allowed;
    }

    &:hover:not(:disabled) {
      opacity: 0.9;
    }
  }
`;

const SectionTitle = styled.div`
  font-weight: 600;
  color: #374151;
  margin: 1rem 0 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  svg {
    width: 1rem;
    height: 1rem;
  }
`;

const Tag = styled.span<{ $type?: string }>`
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  background: ${({ $type }) => {
    switch($type) {
      case 'sci': return '#dbeafe';
      case 'folk': return '#f0fdf4';
      case 'freud': return '#f5f3ff';
      default: return '#e5e7eb';
    }
  }};
  color: ${({ $type }) => {
    switch($type) {
      case 'sci': return '#1d4ed8';
      case 'folk': return '#15803d';
      case 'freud': return '#4f46e5';
      default: return '#374151';
    }
  }};
  margin: 0.25rem;
`;

const LoadingDots = styled.div`
  display: inline-flex;
  gap: 0.25rem;
  
  div {
    width: 0.5rem;
    height: 0.5rem;
    background: #9ca3af;
    border-radius: 50%;
    animation: bounce 1s infinite;

    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }

  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
  }
`;

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { 
      role: "user", 
      content: input 
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) throw new Error(response.statusText);

      const data = await response.json();
      
      const botMessage: Message = {
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        emotions: data.emotions,
        sciTitles: data.sci_titles,
        folkTitles: data.folk_titles,
        freudTitles: data.freud_titles
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "⚠️ 暂时无法获取分析结果，请检查网络连接后重试"
      }]);
    } finally {
      setLoading(false);
    }
  };

  const renderMessageContent = (msg: Message) => {
    const hasMetadata = msg.emotions || msg.sciTitles;

    return (
      <>
        <div className="content">
          {msg.content.split('\n').map((line, i) => (
            <p key={i}>{line}</p>
          ))}

          {hasMetadata && (
            <div className="meta">
              {msg.emotions && (
                <div>
                  <SectionTitle>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z" />
                    </svg>
                    检测情绪
                  </SectionTitle>
                  {msg.emotions.map(e => (
                    <Tag key={e}>{e}</Tag>
                  ))}
                </div>
              )}

              {msg.sciTitles && (
                <div>
                  <SectionTitle>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
                    </svg>
                    相关研究
                  </SectionTitle>
                  {msg.sciTitles.map((t, i) => (
                    <Tag key={i} $type="sci">{t}</Tag>
                  ))}
                </div>
              )}

              {msg.folkTitles && (
                <div>
                  <SectionTitle>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
                    </svg>
                    民俗解读
                  </SectionTitle>
                  {msg.folkTitles.map((t, i) => (
                    <Tag key={i} $type="folk">{t}</Tag>
                  ))}
                </div>
              )}

              {msg.freudTitles && (
                <div>
                  <SectionTitle>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>
                    精神分析
                  </SectionTitle>
                  {msg.freudTitles.map((t, i) => (
                    <Tag key={i} $type="freud">{t}</Tag>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </>
    );
  };

  return (
    <Container>
      <h1 style={{ 
        textAlign: "center",
        marginBottom: "1.5rem",
        color: "#1e40af",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "0.5rem"
      }}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" style={{ width: "1.5rem" }}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.5l-.394-.933a2.25 2.25 0 00-1.423-1.423L13.5 19.5l.933-.394a2.25 2.25 0 001.423-1.423l.394-.933.394.933a2.25 2.25 0 001.423 1.423l.933.394-.933.394a2.25 2.25 0 00-1.423 1.423z" />
        </svg>
        梦境解析专家
      </h1>

      <ChatHistory>
        {messages.map((msg, i) => (
          <MessageBubble key={i} $isUser={msg.role === "user"}>
            {renderMessageContent(msg)}
          </MessageBubble>
        ))}
        {loading && (
          <MessageBubble $isUser={false}>
            <div className="content">
              <LoadingDots>
                <div />
                <div />
                <div />
              </LoadingDots>
            </div>
          </MessageBubble>
        )}
        <div ref={messagesEndRef} />
      </ChatHistory>

      <InputArea>
        <textarea
          value={input}
          placeholder="描述你的梦境（建议包含情绪细节和主要意象）..."
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <button onClick={handleSend} disabled={loading}>
          {loading ? (
            <LoadingDots>
              <div />
              <div />
              <div />
            </LoadingDots>
          ) : (
            <>
              发送
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" style={{ width: "1rem", marginLeft: "0.5rem" }}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
              </svg>
            </>
          )}
        </button>
      </InputArea>
    </Container>
  );
}




























// "use client";

// import { useState } from "react";

// // 定义消息类型
// type Message = {
//   role: "user" | "assistant";
//   content: string;
// };

// export default function Page() {
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);

//   const handleSend = async () => {
//     if (!input.trim()) return;

//     const userMessage: Message = { role: "user", content: input };
//     setMessages((prev) => [...prev, userMessage]);
//     setInput("");
//     setLoading(true);

//     try {
//       const response = await fetch("https://your-api-endpoint.ngrok.io/generate", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ text: userMessage.content }),
//       });

//       const data = await response.json();

//       const botMessage: Message = {
//         role: "assistant",
//         content:
//           data.answer +
//           (data.sources
//             ? "\n\n📚 参考文献:\n" + data.sources.join("\n")
//             : "") +
//           (data.emotions
//             ? "\n\n💡 检测到的情绪: " + data.emotions.join(", ")
//             : ""),
//       };

//       setMessages((prev) => [...prev, botMessage]);
//     } catch (err) {
//       const errorMessage: Message = {
//         role: "assistant",
//         content: "❌ 出错了，无法连接后端接口。请稍后重试。",
//       };
//       setMessages((prev) => [...prev, errorMessage]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
//       <h1 style={{ textAlign: "center", fontSize: "1.5rem", marginBottom: 10 }}>
//         梦境解析对话助手
//       </h1>

//       <div
//         style={{
//           border: "1px solid #ccc",
//           borderRadius: 10,
//           padding: 10,
//           height: 500,
//           overflowY: "scroll",
//           backgroundColor: "#f9f9f9",
//           marginBottom: 10,
//         }}
//       >
//         {messages.map((msg, index) => (
//           <div
//             key={index}
//             style={{
//               textAlign: msg.role === "user" ? "right" : "left",
//               margin: "8px 0",
//             }}
//           >
//             <div
//               style={{
//                 display: "inline-block",
//                 backgroundColor: msg.role === "user" ? "#007bff" : "#e4e6eb",
//                 color: msg.role === "user" ? "white" : "black",
//                 padding: "8px 12px",
//                 borderRadius: 12,
//                 maxWidth: "70%",
//                 whiteSpace: "pre-wrap",
//                 wordBreak: "break-word",
//               }}
//             >
//               {msg.content}
//             </div>
//           </div>
//         ))}
//         {loading && (
//           <div style={{ color: "#888", fontStyle: "italic", paddingTop: 5 }}>
//             正在分析中...
//           </div>
//         )}
//       </div>

//       <div style={{ display: "flex", flexDirection: "column" }}>
//         <textarea
//           style={{
//             width: "100%",
//             height: 80,
//             padding: 8,
//             fontSize: 16,
//             borderRadius: 5,
//             border: "1px solid #ccc",
//             resize: "none",
//           }}
//           value={input}
//           placeholder="请输入梦境描述..."
//           onChange={(e) => setInput(e.target.value)}
//           onKeyDown={(e) => {
//             if (e.key === "Enter" && !e.shiftKey) {
//               e.preventDefault();
//               handleSend();
//             }
//           }}
//         />
//         <button
//           onClick={handleSend}
//           disabled={loading}
//           style={{
//             marginTop: 8,
//             padding: "10px 16px",
//             fontSize: 16,
//             backgroundColor: loading ? "#aaa" : "#28a745",
//             color: "white",
//             border: "none",
//             borderRadius: 5,
//             cursor: loading ? "not-allowed" : "pointer",
//             alignSelf: "flex-end",
//           }}
//         >
//           {loading ? "分析中..." : "发送"}
//         </button>
//       </div>
//     </div>
//   );
// }