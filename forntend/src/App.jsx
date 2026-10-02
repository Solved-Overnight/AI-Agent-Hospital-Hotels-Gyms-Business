import { useEffect, useRef, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const THREAD_STORAGE_KEY = "brightsmile_thread_id";
const AGENT_NAME = "Maya";
const AGENT_ROLE = "BrightSmile AI Receptionist";

const quickPrompts = [
  "What are your opening hours?",
  "What services do you provide?",
  "I want to book an appointment",
];

const initialMessage = {
  role: "assistant",
  content:
    "Hello. Welcome to BrightSmile. I'm Maya, your AI receptionist. How can I help you today?",
};

export default function App() {
  const [chatOpen, setChatOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [messages, setMessages] = useState([initialMessage]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [threadId, setThreadId] = useState(
    () => localStorage.getItem(THREAD_STORAGE_KEY) || ""
  );

const endRef = useRef(null);
const chatOpenRef = useRef(chatOpen);

useEffect(() => {
  chatOpenRef.current = chatOpen;
}, [chatOpen]);

  useEffect(() => {
    if (threadId) {
      localStorage.setItem(THREAD_STORAGE_KEY, threadId);
    } else {
      localStorage.removeItem(THREAD_STORAGE_KEY);
    }
  }, [threadId]);

useEffect(() => {
  if (!chatOpen) return;

  requestAnimationFrame(() => {
    endRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  });
}, [messages, loading, chatOpen]);

async function sendMessage(text) {
  const message = text.trim();

  if (!message || loading) return;

  setMessages((old) => [
    ...old,
    {
      role: "user",
      content: message,
    },
  ]);

  setInput("");
  setLoading(true);

  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        thread_id: threadId || null,
      }),
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data = await response.json();

    setMessages((old) => [
      ...old,
      {
        role: "assistant",
        content: data.response,
      },
    ]);

    /*
     * If Maya replies while the chat is closed,
     * mark the response as unread.
     */
    if (!chatOpenRef.current) {
      setUnreadCount((count) => count + 1);
    }

    if (data.thread_id) {
      setThreadId(data.thread_id);
    }
  } catch (error) {
    console.error(error);

    setMessages((old) => [
      ...old,
      {
        role: "assistant",
        content:
          "I'm having trouble connecting right now. Please try again shortly.",
      },
    ]);

    if (!chatOpenRef.current) {
      setUnreadCount((count) => count + 1);
    }
  } finally {
    setLoading(false);
  }
}

function toggleChat() {
  setChatOpen((open) => {
    const next = !open;

    chatOpenRef.current = next;

    if (next) {
      setUnreadCount(0);
    }

    return next;
  });
}

  function newConversation() {
    localStorage.removeItem(THREAD_STORAGE_KEY);

    setThreadId("");
    setUnreadCount(0);
    setInput("");

    setMessages([initialMessage]);
  }

  return (
    <div className="site">

      {/* ================= NAVIGATION ================= */}

      <header className="navbar">
        <a className="logo" href="#">
          BrightSmile
        </a>

        <nav className="nav-links">
          <a href="#treatments">Treatments</a>
          <a href="#experience">Our approach</a>
          <a href="#doctor">Our team</a>
        </nav>

        <button
          className="nav-cta"
          onClick={() => setChatOpen(true)}
        >
          Book an appointment
        </button>
      </header>


      {/* ================= MAIN ================= */}

      <main>

        {/* HERO */}

        <section className="hero">

          <div className="hero-copy">

            <div className="eyebrow">
              BRIGHTSMILE DENTAL CLINIC
            </div>

            <h1>
              A better smile.
              <br />
              <span>Made simple.</span>
            </h1>

            <p>
              Modern dental care with a calmer, more personal experience.
              From routine care to advanced treatment, we're here to make
              every visit easier.
            </p>

            <div className="hero-actions">

              <button
                className="primary-button"
                onClick={() => setChatOpen(true)}
              >
                Book an appointment
                <span>→</span>
              </button>

              <a
                className="secondary-link"
                href="#treatments"
              >
                Explore treatments
                <span>↓</span>
              </a>

            </div>

          </div>


          <div className="hero-image">

            <div className="hero-image-content">

              <div className="hero-image-label">
                PRECISION · CARE · COMFORT
              </div>

              <div className="smile-mark">
                S
              </div>

              <div className="hero-image-caption">
                <strong>
                  Designed around you.
                </strong>

                <span>
                  Thoughtful dental care, from consultation to treatment.
                </span>
              </div>

            </div>

          </div>

        </section>


        {/* STATEMENT */}

        <section
          className="statement"
          id="experience"
        >

          <div className="statement-small">
            THE BRIGHTSMILE EXPERIENCE
          </div>

          <h2>
            Dentistry doesn't have to feel complicated.
          </h2>

          <p>
            We've designed every part of the experience around clarity,
            comfort, and trust. From your first question to your appointment
            and beyond.
          </p>

        </section>


        {/* FEATURES */}

        <section className="feature-strip">

          <Feature
            number="01"
            title="Personal"
            text="Care shaped around your individual needs."
          />

          <Feature
            number="02"
            title="Precise"
            text="Modern technology supporting better decisions."
          />

          <Feature
            number="03"
            title="Comfortable"
            text="A calmer experience from start to finish."
          />

        </section>


        {/* TREATMENTS */}

        <section
          className="treatments"
          id="treatments"
        >

          <div className="section-top">

            <div>

              <div className="eyebrow">
                WHAT WE DO
              </div>

              <h2>
                Complete dental care.
              </h2>

            </div>

            <p>
              From everyday preventive care to treatments designed
              to transform your smile.
            </p>

          </div>


          <div className="treatment-list">

            <Treatment
              number="01"
              title="General Dentistry"
              text="Routine examinations, preventive care and everyday dental treatment."
            />

            <Treatment
              number="02"
              title="Preventive Care"
              text="Professional cleaning and personalized oral health guidance."
            />

            <Treatment
              number="03"
              title="Cosmetic Dentistry"
              text="Thoughtful treatments designed to help you feel confident about your smile."
            />

            <Treatment
              number="04"
              title="Emergency Care"
              text="Professional guidance when you need dental attention quickly."
            />

          </div>

        </section>


        {/* DOCTOR */}

        <section
          className="doctor-section"
          id="doctor"
        >

          <div className="doctor-visual">
            <div className="doctor-initial">
              DR
            </div>
          </div>

          <div className="doctor-copy">

            <div className="eyebrow">
              OUR DENTAL TEAM
            </div>

            <h2>
              Expertise with a
              <br />
              human touch.
            </h2>

            <p>
              Our dental professionals combine clinical knowledge
              with a patient-first approach.
            </p>

            <div className="doctor-profile">

              <div>
                <strong>
                  Dr. Rahman
                </strong>

                <span>
                  General Dentistry
                </span>
              </div>

              <span className="doctor-active">
                ● Available
              </span>

            </div>

          </div>

        </section>


        {/* FINAL CTA */}

        <section className="final-cta">

          <div className="eyebrow">
            YOUR NEXT VISIT
          </div>

          <h2>
            Your smile is worth
            <br />
            taking care of.
          </h2>

          <button
            className="primary-button light-button"
            onClick={() => setChatOpen(true)}
          >
            Talk to Maya
            <span>→</span>
          </button>

        </section>

      </main>


      {/* ================= FOOTER ================= */}

      <footer>

        <div className="footer-brand">
          BrightSmile
        </div>

        <div className="footer-copy">
          Modern dental care. Human attention.
        </div>

        <div className="footer-year">
          © 2026 BrightSmile Dental Clinic
        </div>

      </footer>


      {/* ================= FLOATING AI BUTTON ================= */}

      <button
        className={`ai-float ${chatOpen ? "active" : ""}`}
        onClick={toggleChat}
        aria-label={chatOpen ? "Close Maya" : "Open Maya"}
      >
        {!chatOpen && (
          <>
            <span className="ai-hover-ring"></span>
            <span className="ai-glow"></span>

            <img
              src="/agent-avatar.png"
              alt="Maya"
              className="floating-agent-image"
            />

            {unreadCount > 0 && (
              <span className="unread-badge">
                {unreadCount > 9 ? "9+" : unreadCount}
              </span>
            )}
          </>
        )}

        {chatOpen && (
          <span className="ai-close-icon">
            ×
          </span>
        )}
      </button>


      {/* ================= AI CHAT ================= */}

      {chatOpen && (

        <div className="chat-popup">

          {/* Header */}

          <div className="chat-popup-header">

            <div className="chat-agent">

              <img
                src="/agent-avatar.png"
                alt={AGENT_NAME}
                className="agent-avatar-image"
              />

              <div>

                <strong>
                  {AGENT_NAME}
                </strong>

                <span>
                  <i></i>
                  {AGENT_ROLE}
                </span>

              </div>

            </div>

            <button
              className="chat-close"
              onClick={() => setChatOpen(false)}
            >
              ×
            </button>

          </div>


          {/* Messages */}

          <div className="chat-popup-body">

            <div className="chat-welcome">

              <div className="welcome-title">
                How can we help?
              </div>

              <div className="welcome-text">
                Ask Maya about our clinic,
                treatments, or appointments.
              </div>

            </div>


            {messages.map((message, index) => (

              <div
                key={`${index}-${message.role}`}
                className={`chat-message ${message.role}`}
              >
                {message.content}
              </div>

            ))}


            {loading && (

              <div className="chat-message assistant typing">

                <span></span>
                <span></span>
                <span></span>

              </div>

            )}

            <div ref={endRef} />

          </div>


          {/* Quick prompts */}

          {messages.length <= 2 && (

            <div className="chat-suggestions">

              {quickPrompts.map((prompt) => (

                <button
                  key={prompt}
                  onClick={() => sendMessage(prompt)}
                  disabled={loading}
                >
                  {prompt}
                </button>

              ))}

            </div>

          )}


          {/* Input */}

          <form
            className="chat-input"
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage(input);
            }}
          >

            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Maya..."
              disabled={loading}
              autoComplete="off"
            />

            <button
              type="submit"
              disabled={!input.trim() || loading}
            >
              ↑
            </button>

          </form>


          {/* Footer */}

          <div className="chat-footer">

            <span>
              AI can make mistakes. For medical advice,
              consult a dental professional.
            </span>

            <button onClick={newConversation}>
              New chat
            </button>

          </div>

        </div>

      )}

    </div>
  );
}


/* ================= COMPONENTS ================= */

function Feature({
  number,
  title,
  text,
}) {
  return (
    <div className="feature">

      <span>
        {number}
      </span>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

    </div>
  );
}


function Treatment({
  number,
  title,
  text,
}) {
  return (
    <div className="treatment">

      <div className="treatment-number">
        {number}
      </div>

      <div className="treatment-main">

        <h3>
          {title}
        </h3>

        <p>
          {text}
        </p>

      </div>

      <div className="treatment-arrow">
        ↗
      </div>

    </div>
  );
}