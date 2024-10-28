"use client";
import Chat from "@/components/Chat";
import ResponseChat from "@/components/ResponseChat";
import { ArrowRight, RefreshCcw, SendIcon } from "lucide-react";
import { useState } from "react";

const bookingID = "03c8788c-b569-49b1-aa91-396d87433057";

const page = () => {
  const [messageData, setMessageData] = useState<any>([]);
  const [inputMsg, setInputMsg] = useState("");
  const [changed, setChanged] = useState(false);
  const [language, setLanguage] = useState("English");
  const [isTyping, setIsTyping] = useState(false); // For showing typing animation

  const handleEnter = async () => {
    if (!inputMsg.trim()) return; // Prevent sending empty messages

    // Show user's message immediately
    setMessageData((prevData: any) => [
      ...prevData,
      { message: inputMsg, sender: "user" },
    ]);

    setInputMsg(""); // Clear the input field

    // Show typing indicator
    setIsTyping(true);

    // Fetch the response
    const restext = await run(inputMsg);

    // Remove typing indicator and display bot's response
    setMessageData((prevData: any) => [
      ...prevData,
      { message: restext, sender: "agent" },
    ]);
    setIsTyping(false);
  };

  async function run(inputMsg: string) {
    const apiUrl = `http://34.19.70.196:5000/api/whatsapp_api/`;
    
    const bodyParams = {
        booking_id: bookingID,
        user_input: inputMsg,
        language: language,
        streaming: false,
    };

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bodyParams),
    });
    
    const result = await response.json();
    const text = result.message; // Assuming the API response format includes 'message' field
    setChanged(true);
    return text;
  }

  const [prevData, setPrevData] = useState([
    [
      { message: "Hello", sender: "user" },
      { message: "Hi", sender: "agent" },
      { message: "How are you?", sender: "user" },
      { message: "I am good", sender: "agent" },
      { message: "What are you doing?", sender: "user" },
    ],
    [
      { message: "I am chatting with you", sender: "agent" },
      { message: "What is your name?", sender: "user" },
      { message: "I am a chatbot", sender: "agent" },
      { message: "What is your purpose?", sender: "user" },
      { message: "I am here to help you", sender: "agent" },
    ],
  ]);

  return (
    <div className="flex min-h-screen justify-between p-24">
      <div className="flex w-1/2 flex-col">
        <div className="text-2xl mb-4">Previous conversations</div>
        <div className="flex flex-col gap-4">
          {prevData.map((data, index) => (
            <div
              key={index}
              className="flex justify-between p-6 rounded-xl border-2 border-slate-800 cursor-pointer"
              onClick={() => setMessageData(data)}
            >
              <div>{data[0].message}</div>
              <ArrowRight size={16} />
            </div>
          ))}
        </div>
      </div>
      <div className="flex flex-col w-1/2 relative">
        <div className="ml-4 h-full border-2 rounded-md relative">
          <div className="p-4 text-xl flex gap-4 items-center absolute w-full">
            <RefreshCcw
              onClick={() => {
                if (changed) setPrevData((prevData) => [...prevData, messageData]);
                setMessageData([]);
              }}
              size={16}
            />
            <div>ChatBot</div>
          </div>
          <div className="p-4 pr-0 justify-end flex flex-col my-12 h-xlg">
            <div className="overflow-auto pr-2">
              {messageData.length > 0 ? (
                messageData.map((e: any, i: number) =>
                  e.sender !== "user" ? (
                    <Chat key={i} msg={e.message} />
                  ) : (
                    <ResponseChat key={i} msg={e.message} />
                  )
                )
              ) : (
                <div className="text-center text-slate-500">
                  Start chatting here!!
                </div>
              )}
              {/* Show typing indicator */}
              {isTyping && (
                <div className="text-slate-500 italic">Typing...</div>
              )}
            </div>
          </div>
          <div className="absolute bottom-0 w-full">
            <div className="relative">
              <input
                type="text"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleEnter();
                  }
                }}
                value={inputMsg}
                onChange={(e) => setInputMsg(e.target.value)}
                className="w-full p-4 border-t-2 border-gray-300 text-slate-950"
                placeholder="Type your message here"
              />
              <select
                className="absolute right-24 top-1 z-50 bg-slate-900 rounded-xl p-2 text-white"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="English">English</option>
                <option value="Spanish">Hindi</option>
                <option value="French">Kannada</option>
                {/* Add more language options as needed */}
              </select>
              <button
                className="absolute right-2 top-1 z-50 bg-slate-900 rounded-xl p-4"
                onClick={handleEnter}
              >
                <SendIcon size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default page;
