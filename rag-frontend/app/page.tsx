// "use client";

// import { useState, useRef, useEffect } from "react";
// import styled from "styled-components";

// // 类型定义
// type Message = {
//   role: "user" | "assistant";
//   content: string;
//   sources?: string[];
//   emotions?: string[];
//   sciTitles?: string[];
//   folkTitles?: string[];
//   freudTitles?: string[];
// };

// // 样式组件
// const Container = styled.div`
//   max-width: 800px;
//   margin: 0 auto;
//   padding: 2rem;
//   height: 100vh;
//   display: flex;
//   flex-direction: column;
// `;

// const ChatHistory = styled.div`
//   flex: 1;
//   overflow-y: auto;
//   background: #f8f9fa;
//   border-radius: 12px;
//   padding: 1.5rem;
//   box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
//   margin-bottom: 1rem;
// `;

// const MessageBubble = styled.div<{ $isUser: boolean }>`
//   display: flex;
//   flex-direction: column;
//   margin: 0.8rem 0;
//   align-items: ${({ $isUser }) => $isUser ? 'flex-end' : 'flex-start'};

//   .content {
//     max-width: 85%;
//     padding: 1rem 1.2rem;
//     border-radius: ${({ $isUser }) => 
//       $isUser ? '15px 15px 0 15px' : '15px 15px 15px 0'};
//     background: ${({ $isUser }) => 
//       $isUser ? '#3b82f6' : 'white'};
//     color: ${({ $isUser }) => $isUser ? 'white' : '#1f2937'};
//     box-shadow: 0 2px 8px rgba(0,0,0,0.1);
//     line-height: 1.6;
//   }

//   .meta {
//     font-size: 0.8rem;
//     color: #6b7280;
//     margin-top: 0.5rem;
//     display: flex;
//     gap: 0.5rem;
//   }
// `;

// const InputArea = styled.div`
//   position: relative;
//   border: 2px solid #e5e7eb;
//   border-radius: 12px;
//   transition: border-color 0.2s;

//   &:focus-within {
//     border-color: #3b82f6;
//   }

//   textarea {
//     width: 100%;
//     padding: 1rem 4rem 1rem 1rem;
//     border: none;
//     border-radius: 12px;
//     resize: none;
//     font-size: 1rem;
//     min-height: 100px;

//     &:focus {
//       outline: none;
//     }
//   }

//   button {
//     position: absolute;
//     bottom: 1rem;
//     right: 1rem;
//     padding: 0.5rem 1rem;
//     background: #3b82f6;
//     color: white;
//     border: none;
//     border-radius: 8px;
//     cursor: pointer;
//     transition: opacity 0.2s;

//     &:disabled {
//       background: #9ca3af;
//       cursor: not-allowed;
//     }

//     &:hover:not(:disabled) {
//       opacity: 0.9;
//     }
//   }
// `;

// const SectionTitle = styled.div`
//   font-weight: 600;
//   color: #374151;
//   margin: 1rem 0 0.5rem;
//   display: flex;
//   align-items: center;
//   gap: 0.5rem;

//   svg {
//     width: 1rem;
//     height: 1rem;
//   }
// `;

// const Tag = styled.span<{ $type?: string }>`
//   display: inline-flex;
//   align-items: center;
//   padding: 0.25rem 0.75rem;
//   border-radius: 20px;
//   font-size: 0.75rem;
//   background: ${({ $type }) => {
//     switch($type) {
//       case 'sci': return '#dbeafe';
//       case 'folk': return '#f0fdf4';
//       case 'freud': return '#f5f3ff';
//       default: return '#e5e7eb';
//     }
//   }};
//   color: ${({ $type }) => {
//     switch($type) {
//       case 'sci': return '#1d4ed8';
//       case 'folk': return '#15803d';
//       case 'freud': return '#4f46e5';
//       default: return '#374151';
//     }
//   }};
//   margin: 0.25rem;
// `;

// const LoadingDots = styled.div`
//   display: inline-flex;
//   gap: 0.25rem;
  
//   div {
//     width: 0.5rem;
//     height: 0.5rem;
//     background: #9ca3af;
//     border-radius: 50%;
//     animation: bounce 1s infinite;

//     &:nth-child(2) {
//       animation-delay: 0.2s;
//     }
//     &:nth-child(3) {
//       animation-delay: 0.4s;
//     }
//   }

//   @keyframes bounce {
//     0%, 100% { transform: translateY(0); }
//     50% { transform: translateY(-4px); }
//   }
// `;

// export default function ChatInterface() {
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);
//   const messagesEndRef = useRef<HTMLDivElement>(null);

//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   const handleSend = async () => {
//     if (!input.trim() || loading) return;

//     const userMessage: Message = { 
//       role: "user", 
//       content: input 
//     };
    
//     setMessages(prev => [...prev, userMessage]);
//     setInput("");
//     setLoading(true);

//     try {
//       const response = await fetch("http://localhost:8000/analyze", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ text: input }),
//       });

//       if (!response.ok) throw new Error(response.statusText);

//       const data = await response.json();
//       const botMessage: Message = {
//         role: "assistant",
//         content: data.answer,
//         sources: data.sources,
//         emotions: data.emotions,
//         sciTitles: data.sciTitles,
//         folkTitles: data.folkTitles,
//         freudTitles: data.freudTitles
//       };

//       setMessages(prev => [...prev, botMessage]);
//     } catch (err) {
//       setMessages(prev => [...prev, {
//         role: "assistant",
//         content: "⚠️ Unable to obtain analysis results temporarily, please check the network connection and try again"
//       }]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const renderMessageContent = (msg: Message) => {
//     const hasMetadata = msg.emotions || msg.sciTitles;

//     return (
//       <>
//         <div className="content">
//           {msg.content.split('\n').map((line, i) => (
//             <p key={i}>{line}</p>
//           ))}

//           {hasMetadata && (
//             <div className="meta">
//               {msg.emotions && msg.emotions.map(e => <Tag key={e}>{e}</Tag>)}
//               {msg.sciTitles && msg.sciTitles.map(t => <Tag key={t} $type="sci">{t}</Tag>)}
//               {msg.folkTitles && msg.folkTitles.map(t => <Tag key={t} $type="folk">{t}</Tag>)}
//               {msg.freudTitles && msg.freudTitles.map(t => <Tag key={t} $type="freud">{t}</Tag>)}
//             </div>
//           )}
//         </div>
//       </>
//     );
//   };

//   return (
//     <Container>
//       <h1 style={{ textAlign: "center", marginBottom: "1.5rem", color: "#1e40af" }}>Dream analysis expert</h1>

//       <ChatHistory>
//         {messages.map((msg, i) => (
//           <MessageBubble key={i} $isUser={msg.role === "user"}>
//             {renderMessageContent(msg)}
//           </MessageBubble>
//         ))}
//         {loading && (
//           <MessageBubble $isUser={false}>
//             <div className="content">
//               <LoadingDots>
//                 <div /> <div /> <div />
//               </LoadingDots>
//             </div>
//           </MessageBubble>
//         )}
//         <div ref={messagesEndRef} />
//       </ChatHistory>

//       <InputArea>
//         <textarea
//           value={input}
//           placeholder="Describe your dream (emotional details and key imagery are recommended)..."
//           onChange={(e) => setInput(e.target.value)}
//           onKeyDown={(e) => {
//             if (e.key === "Enter" && !e.shiftKey) {
//               e.preventDefault();
//               handleSend();
//             }
//           }}
//         />
//         <button onClick={handleSend} disabled={loading}>
//           {loading ? (
//             <LoadingDots><div /> <div /> <div /></LoadingDots>
//           ) : (
//             <>发送</>
//           )}
//         </button>
//       </InputArea>
//     </Container>
//   );
// }

// app/page.tsx
import ChatInterface from './components/chat-interface';
import { ThemeToggle } from './components/theme-toggle';

export default function Home() {
  return (
    <main>
      <ThemeToggle />
      <ChatInterface />
    </main>
  );
}

