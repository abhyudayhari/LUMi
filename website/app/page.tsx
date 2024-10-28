"use client";
import Chat from "@/components/Chat";
import ResponseChat from "@/components/ResponseChat";
import { useState, useEffect } from "react";
import { ArrowLeftCircle, ArrowRight, Mic } from "lucide-react";
import { collection, doc, getDocs, setDoc } from "firebase/firestore";
import { db } from "./firebase";
import { toast } from "react-toastify";

import "react-toastify/dist/ReactToastify.css";

export default function Home() {
  const [callStatus, setCallStatus] = useState("Waiting for call");
  const [isAIResponse, setIsAIResponse] = useState(false);
  const [messageData, setMessageData] = useState<any>([]);
  const [prevCallsData, setPrevCallsData] = useState<any>([]);

  const [currHistory, setCurrHistory] = useState<any>([]);
  useEffect(() => {
    if (callStatus === "Call Ended") {
      return;
    }

    const fetchCallStatus = async () => {
      try {
        const response = await fetch("/api/call");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setIsAIResponse(data.isAIResponse);
        if (data.isChatMessage) {
          setMessageData((prevData: any) => [...prevData, data.chatMessage]);
        }
        if (data.isCallEnded) {
          setCallStatus("Call Ended");
          return;
        }
        setCallStatus(data.isCallOngoing ? "Call Ongoing" : "Waiting for call");
      } catch (error) {
        console.error("Error fetching call status:", error);
      }
    };

    const intervalId = setInterval(fetchCallStatus, 2000);

    return () => clearInterval(intervalId);
  }, [callStatus]);

  const parseAIResponse = (response: string) => {
    return response.replace(/<say>|<\/say>/g, "");
  };
  const getCallsData = async () => {
    try {
      const callsRef = collection(db, "calls");
      const callsSnapshot = await getDocs(callsRef);
      const callsData = callsSnapshot.docs.map((doc) => {
        return { data: doc.data(), docId: doc.id };
      });
      setPrevCallsData(callsData);
    } catch (error) {
      console.error("Error fetching calls data:", error);
    }
  };

  useEffect(() => {
    getCallsData();
  }, []);
  const clearHistory = () => {
    setCurrHistory([]);
  };
  return (
    <main className="flex flex-col md:flex-row min-h-screen justify-between p-6 md:p-24">
      {currHistory.data && (
        <div className="fixed inset-0 bg-black z-40 p-4 md:p-12 overflow-y-auto">
          <div className="flex flex-col md:flex-row text-lg md:text-xl justify-between mb-4 text-white">
            <div className="flex items-center gap-4 mb-4 md:mb-0">
              <div onClick={clearHistory} className="cursor-pointer">
                <ArrowLeftCircle />
              </div>
              Transcription History
            </div>
            <div>{currHistory.data.callStatus}</div>
          </div>
          <div>
            {currHistory.data.messages.map((data: any, index: number) => {
              return index % 2 == 0 ? (
                <Chat key={index} msg={data} />
              ) : (
                <ResponseChat key={index} msg={data} />
              );
            })}
          </div>
        </div>
      )}
      <div className="flex flex-col w-full md:w-1/2 justify-between mb-8 md:mb-0">
        <div
          className="h-40 md:h-1/2 text-2xl md:text-4xl text-center flex flex-col items-center justify-center gap-4"
          onClick={async () => {
            setCallStatus("Call Ended");
            const dateAndTimeNow = new Date().toLocaleString();
            const dateAndTimeNowFormatted = dateAndTimeNow.replace(/\//g, "-");

            try {
              await setDoc(doc(db, "calls", dateAndTimeNowFormatted), {
                callStatus: "Call Ended",
                callTime: dateAndTimeNowFormatted,
                messages: messageData,
              });
              toast.success("Call Ended Successfully!");
            } catch (e) {
              console.error("Error writing document: ", e);
              toast.error("Error writing document");
            }
          }}
        >
          {callStatus === "Call Ongoing" ? (
            <div className="p-4 glow-icon rounded-full">
              <Mic size={64} />
            </div>
          ) : null}
          {callStatus}
        </div>
        <div className="h-40 md:h-auto overflow-auto">
          <div className="mb-2 text-lg md:text-xl">Previous calls</div>
          <div>
            <div className="flex flex-col gap-4">
              {prevCallsData.map((data: any, index: number) => {
                return (
                  <div
                    key={index}
                    onClick={() => {
                      setCurrHistory(data);
                    }}
                    className="flex justify-between items-center border-2 border-slate-800 rounded-md p-4 cursor-pointer"
                  >
                    <div>{data.docId}</div>
                    <ArrowRight size={16} className="cursor-pointer" />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      <div className="flex flex-col w-full md:w-1/2 relative">
        <div className="h-full border-2 rounded-md">
          <div className="p-4 text-lg md:text-xl w-full">Live transcription</div>
          <div className="p-4 pr-0 flex flex-col justify-end mt-12 h-[400px] md:h-xxlg">
            <div className="overflow-auto pr-2">
              {messageData.length > 0 ? (
                messageData.map((e: string, i: number) =>
                  i % 2 !== 0 ? (
                    <Chat msg={parseAIResponse(e)} />
                  ) : (
                    <ResponseChat msg={e} />
                  )
                )
              ) : (
                <div className="text-center text-slate-500">
                  Start a phone call to start receiving messages
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
