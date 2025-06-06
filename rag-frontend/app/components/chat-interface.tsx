"use client"

import { useState, useRef, useEffect } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { Moon, Sun, Send, Brain, Book, Sparkles, Loader2, ChevronDown, MessageSquare, Stars, Zap } from "lucide-react"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"

// Types
type Message = {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: string[]
  emotions?: string[]
  sciTitles?: string[]
  folkTitles?: string[]
  freudTitles?: string[]
  timestamp: Date
}

type Analysis = {
  scientific: {
    title: string
    content: string
  }[]
  folk: {
    title: string
    content: string
  }[]
  freudian: {
    title: string
    content: string
  }[]
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [currentAnalysis, setCurrentAnalysis] = useState<Analysis | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { theme, setTheme } = useTheme()
  const [language, setLanguage] = useState<"en" | "zh">("en")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Sample welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: "welcome",
          role: "assistant",
          content:
            language === "en"
              ? "✨ Welcome to Dream Analysis AI. I'm here to help you explore the hidden meanings in your dreams through scientific research, cultural symbolism, and psychological insights. Share your dream with me..."
              : "✨ 欢迎使用梦境分析AI。我将通过科学研究、文化象征和心理学见解帮助您探索梦境中的隐藏含义。与我分享您的梦境吧...",
          timestamp: new Date(),
        },
      ])
    }
  }, [language, messages.length])

  // 在 ChatInterface 函数的顶部添加：
  const [stars, setStars] = useState<
    { left: string; top: string; delay: number; duration: number }[]
  >([]);

  useEffect(() => {
    const newStars = [...Array(20)].map(() => ({
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      delay: Math.random() * 2,
      duration: 2 + Math.random() * 2,
    }));
    setStars(newStars);
  }, []);


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + "px"
    }
  }, [input])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: input,
          language,
        }),
      })

      if (!response.ok) throw new Error(response.statusText)

      const data = await response.json()

      // Create mock analysis data for demo purposes
      const mockAnalysis: Analysis = {
        scientific:
          data.sciTitles?.map((title: string) => ({
            title,
            content:
              "Scientific analysis of dream patterns suggests connections to memory consolidation and emotional processing during REM sleep cycles.",
          })) || [],
        folk:
          data.folkTitles?.map((title: string) => ({
            title,
            content:
              "Cultural interpretations often connect these symbols to life transitions, spiritual journeys, and collective unconscious patterns.",
          })) || [],
        freudian:
          data.freudTitles?.map((title: string) => ({
            title,
            content:
              "From a psychoanalytic perspective, these elements may represent unconscious desires, repressed memories, and symbolic wish fulfillment.",
          })) || [],
      }

      setCurrentAnalysis(mockAnalysis)

      const botMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        emotions: data.emotions,
        sciTitles: data.sciTitles,
        folkTitles: data.folkTitles,
        freudTitles: data.freudTitles,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, botMessage])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "assistant",
          content:
            language === "en"
              ? "⚠️ Unable to analyze your dream at the moment. Please check your connection and try again."
              : "⚠️ 暂时无法分析您的梦境，请检查网络连接并重试。",
          timestamp: new Date(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === "en" ? "zh" : "en"))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-60 h-60 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-4000"></div>

        {/* Floating stars
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full opacity-60"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0.3, 1, 0.3],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2 + Math.random() * 2,
              repeat: Number.POSITIVE_INFINITY,
              delay: Math.random() * 2,
            }}
          />
        ))} */}


        {/* Floating stars (fixed for hydration) */}
        {stars.map((star, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full opacity-60"
            style={{ left: star.left, top: star.top }}
            animate={{
              opacity: [0.3, 1, 0.3],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: star.duration,
              repeat: Number.POSITIVE_INFINITY,
              delay: star.delay,
            }}
          />
        ))}

      </div>

      <div className="relative z-10 container mx-auto p-4 max-w-7xl h-screen flex flex-col">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between py-6 border-b border-white/10 backdrop-blur-sm"
        >
          <div className="flex items-center gap-3">
            <div className="relative">
              <Moon className="h-8 w-8 text-purple-300" />
              <Stars className="h-4 w-4 text-yellow-300 absolute -top-1 -right-1" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-200 via-pink-200 to-blue-200 bg-clip-text text-transparent">
                {language === "en" ? "Dream Analysis AI" : "梦境分析AI"}
              </h1>
              <p className="text-purple-200/70 text-sm">
                {language === "en" ? "Unlock the mysteries of your subconscious" : "解锁您潜意识的奥秘"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleLanguage}
              className="text-purple-200 hover:bg-white/10 border border-white/20"
            >
              {language === "en" ? "中文" : "English"}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="text-purple-200 hover:bg-white/10 border border-white/20"
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </div>
        </motion.header>

        <div className="grid flex-1 gap-6 lg:grid-cols-4 overflow-hidden mt-6">
          {/* Main Chat Area */}
          <div className="lg:col-span-3 flex flex-col h-full">
            <div className="flex-1 relative">
              <ScrollArea className="h-full pr-4">
                <div className="space-y-6 pb-4">
                  <AnimatePresence>
                    {messages.map((msg) => (
                      <motion.div
                        key={msg.id}
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ duration: 0.4, ease: "easeOut" }}
                        className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}
                      >
                        <div
                          className={cn(
                            "max-w-[85%] rounded-2xl p-4 shadow-lg backdrop-blur-sm",
                            msg.role === "user"
                              ? "bg-gradient-to-r from-purple-500/90 to-pink-500/90 text-white border border-purple-300/30"
                              : "bg-white/10 text-purple-50 border border-white/20",
                          )}
                        >
                          <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>

                          {msg.emotions && msg.emotions.length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-2">
                              {msg.emotions.map((emotion) => (
                                <Badge
                                  key={emotion}
                                  variant="secondary"
                                  className="bg-white/20 text-purple-100 border-white/30 text-xs"
                                >
                                  {emotion}
                                </Badge>
                              ))}
                            </div>
                          )}

                          <div className="text-xs opacity-60 mt-2 flex items-center gap-2">
                            <span>{msg.timestamp.toLocaleTimeString()}</span>
                            {msg.role === "assistant" && <Sparkles className="h-3 w-3" />}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>

                  {loading && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex justify-start"
                    >
                      <div className="bg-white/10 backdrop-blur-sm max-w-[85%] rounded-2xl p-4 border border-white/20">
                        <div className="flex items-center gap-3">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-purple-300 rounded-full animate-bounce"></div>
                            <div
                              className="w-2 h-2 bg-pink-300 rounded-full animate-bounce"
                              style={{ animationDelay: "0.1s" }}
                            ></div>
                            <div
                              className="w-2 h-2 bg-blue-300 rounded-full animate-bounce"
                              style={{ animationDelay: "0.2s" }}
                            ></div>
                          </div>
                          <span className="text-purple-200">
                            {language === "en" ? "Analyzing your dream..." : "正在分析您的梦境..."}
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
                <div ref={messagesEndRef} />
              </ScrollArea>
            </div>

            {/* ChatGPT-style Input */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mt-4">
              <div className="relative max-w-4xl mx-auto">
                <div className="relative flex items-end bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 shadow-2xl">
                  <Textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={language === "en" ? "Describe your dream in detail..." : "详细描述您的梦境..."}
                    className="flex-1 min-h-[50px] max-h-[200px] bg-transparent border-0 resize-none text-purple-50 placeholder:text-purple-200/50 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-2xl p-4 pr-12"
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault()
                        handleSend()
                      }
                    }}
                  />
                  <Button
                    onClick={handleSend}
                    disabled={loading || !input.trim()}
                    size="icon"
                    className="absolute right-2 bottom-2 h-8 w-8 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 border-0 shadow-lg disabled:opacity-50"
                  >
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  </Button>
                </div>
                <div className="text-center mt-2">
                  <span className="text-xs text-purple-200/60">
                    {language === "en"
                      ? "Press Enter to send, Shift + Enter for new line"
                      : "按Enter发送，Shift + Enter换行"}
                  </span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="hidden lg:block"
          >
            <div className="bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 h-full overflow-hidden">
              <Tabs defaultValue="insights" className="h-full flex flex-col">
                <TabsList className="grid w-full grid-cols-3 bg-white/10 m-2">
                  <TabsTrigger value="insights" className="data-[state=active]:bg-purple-500/50 text-purple-100">
                    <Brain className="h-4 w-4 mr-1" />
                    {language === "en" ? "Insights" : "见解"}
                  </TabsTrigger>
                  <TabsTrigger value="sources" className="data-[state=active]:bg-purple-500/50 text-purple-100">
                    <Book className="h-4 w-4 mr-1" />
                    {language === "en" ? "Sources" : "来源"}
                  </TabsTrigger>
                  <TabsTrigger value="symbols" className="data-[state=active]:bg-purple-500/50 text-purple-100">
                    <Sparkles className="h-4 w-4 mr-1" />
                    {language === "en" ? "Symbols" : "符号"}
                  </TabsTrigger>
                </TabsList>

                <div className="flex-1 overflow-hidden">
                  <TabsContent value="insights" className="h-full p-4 space-y-4 overflow-y-auto">
                    <h3 className="text-lg font-medium text-purple-100">
                      {language === "en" ? "Analysis Insights" : "分析见解"}
                    </h3>

                    {currentAnalysis ? (
                      <>
                        {currentAnalysis.scientific.length > 0 && (
                          <Collapsible className="bg-white/5 rounded-xl border border-white/10">
                            <CollapsibleTrigger className="flex items-center justify-between w-full p-3 font-medium text-purple-100 hover:bg-white/5">
                              <div className="flex items-center">
                                <Zap className="h-4 w-4 mr-2 text-blue-400" />
                                {language === "en" ? "Scientific" : "科学视角"}
                              </div>
                              <ChevronDown className="h-4 w-4" />
                            </CollapsibleTrigger>
                            <CollapsibleContent className="p-3 pt-0">
                              {currentAnalysis.scientific.map((item, i) => (
                                <Card key={i} className="mb-2 bg-white/5 border-white/10">
                                  <CardContent className="p-3">
                                    <h4 className="font-medium text-sm text-purple-100">{item.title}</h4>
                                    <p className="text-sm text-purple-200/70 mt-1">{item.content}</p>
                                  </CardContent>
                                </Card>
                              ))}
                            </CollapsibleContent>
                          </Collapsible>
                        )}

                        {currentAnalysis.folk.length > 0 && (
                          <Collapsible className="bg-white/5 rounded-xl border border-white/10">
                            <CollapsibleTrigger className="flex items-center justify-between w-full p-3 font-medium text-purple-100 hover:bg-white/5">
                              <div className="flex items-center">
                                <Book className="h-4 w-4 mr-2 text-green-400" />
                                {language === "en" ? "Cultural" : "文化象征"}
                              </div>
                              <ChevronDown className="h-4 w-4" />
                            </CollapsibleTrigger>
                            <CollapsibleContent className="p-3 pt-0">
                              {currentAnalysis.folk.map((item, i) => (
                                <Card key={i} className="mb-2 bg-white/5 border-white/10">
                                  <CardContent className="p-3">
                                    <h4 className="font-medium text-sm text-purple-100">{item.title}</h4>
                                    <p className="text-sm text-purple-200/70 mt-1">{item.content}</p>
                                  </CardContent>
                                </Card>
                              ))}
                            </CollapsibleContent>
                          </Collapsible>
                        )}

                        {currentAnalysis.freudian.length > 0 && (
                          <Collapsible className="bg-white/5 rounded-xl border border-white/10">
                            <CollapsibleTrigger className="flex items-center justify-between w-full p-3 font-medium text-purple-100 hover:bg-white/5">
                              <div className="flex items-center">
                                <Sparkles className="h-4 w-4 mr-2 text-purple-400" />
                                {language === "en" ? "Psychological" : "心理学"}
                              </div>
                              <ChevronDown className="h-4 w-4" />
                            </CollapsibleTrigger>
                            <CollapsibleContent className="p-3 pt-0">
                              {currentAnalysis.freudian.map((item, i) => (
                                <Card key={i} className="mb-2 bg-white/5 border-white/10">
                                  <CardContent className="p-3">
                                    <h4 className="font-medium text-sm text-purple-100">{item.title}</h4>
                                    <p className="text-sm text-purple-200/70 mt-1">{item.content}</p>
                                  </CardContent>
                                </Card>
                              ))}
                            </CollapsibleContent>
                          </Collapsible>
                        )}
                      </>
                    ) : (
                      <div className="text-center p-8 text-purple-200/60">
                        <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-30" />
                        <p className="text-sm">
                          {language === "en" ? "Share your dream to see insights" : "分享您的梦境以查看见解"}
                        </p>
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="sources" className="h-full p-4 overflow-y-auto">
                    <h3 className="text-lg font-medium mb-4 text-purple-100">
                      {language === "en" ? "Reference Sources" : "参考来源"}
                    </h3>
                    <div className="space-y-3">
                      {[
                        { title: "The Interpretation of Dreams", author: "Sigmund Freud", type: "Classic" },
                        { title: "Man and His Symbols", author: "Carl Jung", type: "Psychology" },
                        { title: "The Neuroscience of Sleep", author: "Research", type: "Science" },
                        { title: "Cultural Dream Symbolism", author: "Anthropology", type: "Culture" },
                      ].map((source, i) => (
                        <Card
                          key={i}
                          className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors cursor-pointer"
                        >
                          <CardContent className="p-3">
                            <div className="flex justify-between items-start">
                              <div>
                                <h4 className="font-medium text-sm text-purple-100">{source.title}</h4>
                                <p className="text-xs text-purple-200/70">{source.author}</p>
                              </div>
                              <Badge variant="outline" className="text-xs border-purple-300/30 text-purple-200">
                                {source.type}
                              </Badge>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>

                  <TabsContent value="symbols" className="h-full p-4 overflow-y-auto">
                    <h3 className="text-lg font-medium mb-4 text-purple-100">
                      {language === "en" ? "Dream Symbols" : "梦境符号"}
                    </h3>
                    <div className="grid gap-3">
                      {[
                        { symbol: "🌊 Water", meaning: "Emotions, unconscious mind" },
                        { symbol: "🕊️ Flying", meaning: "Freedom, transcendence" },
                        { symbol: "🏠 House", meaning: "Self, identity, psyche" },
                        { symbol: "🐍 Snake", meaning: "Transformation, wisdom" },
                        { symbol: "🌙 Moon", meaning: "Intuition, feminine energy" },
                        { symbol: "🔥 Fire", meaning: "Passion, purification" },
                      ].map((item, i) => (
                        <Card key={i} className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors">
                          <CardContent className="p-3">
                            <h4 className="font-medium text-purple-100 text-sm">{item.symbol}</h4>
                            <p className="text-xs text-purple-200/70 mt-1">{item.meaning}</p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>
                </div>
              </Tabs>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
