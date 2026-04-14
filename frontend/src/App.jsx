import { useEffect, useMemo, useState } from "react";
import { api } from "./api";

const emptySignupForm = {
  name: "",
  email: "",
  password: "",
  bio: "",
  profile_photo_url: "",
  city: "",
};

const emptyLoginForm = {
  email: "",
  password: "",
};

const emptyProfileForm = {
  name: "",
  bio: "",
  profile_photo_url: "",
  city: "",
};

const emptySkillForm = {
  title: "",
  category: "",
  description: "",
  skill_type: "offer",
  proficiency_level: "",
  availability: "",
};

function toPayload(values) {
  return Object.fromEntries(
    Object.entries(values).filter(([, value]) => value !== "" && value !== undefined),
  );
}

function TagList({ tags = [] }) {
  if (!tags.length) {
    return null;
  }

  return (
    <div className="tag-list">
      {tags.map((tag) => (
        <span className="tag-chip" key={tag}>
          {tag}
        </span>
      ))}
    </div>
  );
}

function AuthForm({ mode, onModeChange, onSubmit, loading, error }) {
  const [form, setForm] = useState(mode === "signup" ? emptySignupForm : emptyLoginForm);

  useEffect(() => {
    setForm(mode === "signup" ? emptySignupForm : emptyLoginForm);
  }, [mode]);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await onSubmit(form);
  }

  return (
    <section className="auth-shell">
      <div className="hero-card">
        <p className="eyebrow">LLM-enabled marketplace</p>
        <h1>Trade practical skills with better matching, smarter listings, and direct chat.</h1>
        <p className="hero-copy">
          Create cleaner listings with AI assistance, search in natural language, review
          semantic matches, and message once an exchange request is accepted.
        </p>
      </div>
      <form className="panel auth-panel" onSubmit={handleSubmit}>
        <div className="panel-heading">
          <h2>{mode === "signup" ? "Create account" : "Welcome back"}</h2>
          <p>
            {mode === "signup"
              ? "Set up your profile to start listing skills."
              : "Sign in with your existing account."}
          </p>
        </div>

        {mode === "signup" ? (
          <>
            <label>
              Name
              <input name="name" value={form.name} onChange={updateField} required />
            </label>
            <label>
              Email
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={updateField}
                required
              />
            </label>
            <label>
              Password
              <input
                name="password"
                type="password"
                value={form.password}
                onChange={updateField}
                minLength={8}
                required
              />
            </label>
            <label>
              City
              <input name="city" value={form.city} onChange={updateField} />
            </label>
            <label>
              Bio
              <textarea name="bio" value={form.bio} onChange={updateField} rows="4" />
            </label>
            <label>
              Profile photo URL
              <input
                name="profile_photo_url"
                type="url"
                value={form.profile_photo_url}
                onChange={updateField}
              />
            </label>
          </>
        ) : (
          <>
            <label>
              Email
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={updateField}
                required
              />
            </label>
            <label>
              Password
              <input
                name="password"
                type="password"
                value={form.password}
                onChange={updateField}
                minLength={8}
                required
              />
            </label>
          </>
        )}

        {error ? <p className="form-error">{error}</p> : null}

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Submitting..." : mode === "signup" ? "Create account" : "Sign in"}
        </button>

        <button
          className="ghost-button"
          type="button"
          onClick={() => onModeChange(mode === "signup" ? "login" : "signup")}
        >
          {mode === "signup"
            ? "Already have an account? Sign in"
            : "Need an account? Create one"}
        </button>
      </form>
    </section>
  );
}

function ProfilePanel({ profile, onSave, loading }) {
  const [form, setForm] = useState(emptyProfileForm);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!profile) {
      return;
    }
    setForm({
      name: profile.name || "",
      bio: profile.bio || "",
      profile_photo_url: profile.profile_photo_url || "",
      city: profile.city || "",
    });
  }, [profile]);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    if (message) {
      setMessage("");
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await onSave(form);
    setMessage("Profile updated.");
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Profile</h2>
        <p>Keep your public details current so search and match suggestions stay accurate.</p>
      </div>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Name
          <input name="name" value={form.name} onChange={updateField} required />
        </label>
        <label>
          City
          <input name="city" value={form.city} onChange={updateField} />
        </label>
        <label>
          Profile photo URL
          <input
            name="profile_photo_url"
            type="url"
            value={form.profile_photo_url}
            onChange={updateField}
          />
        </label>
        <label>
          Bio
          <textarea name="bio" value={form.bio} onChange={updateField} rows="4" />
        </label>
        <div className="inline-actions">
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Saving..." : "Save profile"}
          </button>
          {message ? <span className="helper-text">{message}</span> : null}
        </div>
      </form>
    </section>
  );
}

function SkillForm({ onSubmit, onAssist, loading, assisting }) {
  const [form, setForm] = useState(emptySkillForm);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await onSubmit(form, () => setForm(emptySkillForm));
  }

  async function handleAssist() {
    if (!form.description.trim() || form.description.trim().length < 4) {
      return;
    }
    const suggestion = await onAssist(form);
    if (suggestion) {
      setForm({
        title: suggestion.title || "",
        category: suggestion.category || "",
        description: suggestion.description || form.description,
        skill_type: suggestion.skill_type || form.skill_type,
        proficiency_level: suggestion.proficiency_level || "",
        availability: suggestion.availability || "",
      });
    }
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <label>
        Title
        <input name="title" value={form.title} onChange={updateField} required />
      </label>
      <label>
        Category
        <input name="category" value={form.category} onChange={updateField} required />
      </label>
      <label>
        Type
        <select name="skill_type" value={form.skill_type} onChange={updateField}>
          <option value="offer">Offer</option>
          <option value="request">Request</option>
        </select>
      </label>
      <label>
        Proficiency level
        <input
          name="proficiency_level"
          value={form.proficiency_level}
          onChange={updateField}
        />
      </label>
      <label>
        Availability
        <input name="availability" value={form.availability} onChange={updateField} />
      </label>
      <label>
        Description
        <textarea
          name="description"
          value={form.description}
          onChange={updateField}
          rows="4"
          minLength={10}
          required
        />
      </label>
      <div className="inline-actions">
        <button
          className="primary-button"
          type="button"
          onClick={handleAssist}
          disabled={assisting || form.description.trim().length < 4}
        >
          {assisting ? "Generating..." : "Use AI assistant"}
        </button>
        <button className="ghost-button" type="submit" disabled={loading}>
          {loading ? "Saving..." : "Add skill"}
        </button>
      </div>
    </form>
  );
}

function SearchPanel({ results, loading, onSearch }) {
  const [query, setQuery] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    await onSearch(query);
  }

  return (
    <section className="panel panel-wide">
      <div className="panel-heading">
        <h2>Natural language search</h2>
        <p>Search like a person: “Need a React mentor in Kolkata on weekends.”</p>
      </div>
      <form className="search-row" onSubmit={handleSubmit}>
        <input
          placeholder="Describe the skill, city, schedule, or format you want"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button className="primary-button" type="submit" disabled={loading || query.length < 2}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>
      <div className="card-list">
        {results.length === 0 ? (
          <p className="empty-state">No search results yet. Run a natural-language query above.</p>
        ) : null}
        {results.map((result) => (
          <article className="item-card" key={result.skill.id}>
            <div className="item-header">
              <strong>{result.skill.title}</strong>
              <span className="pill pill-offer">score {Math.round(result.score * 100)}%</span>
            </div>
            <p>{result.skill.description}</p>
            {result.skill.ai_summary ? <p className="meta-block">{result.skill.ai_summary}</p> : null}
            <p className="meta-line">
              {result.skill.owner.name}
              {result.skill.owner.city ? ` • ${result.skill.owner.city}` : ""}
              {result.skill.availability ? ` • ${result.skill.availability}` : ""}
            </p>
            <p className="helper-text">{result.rationale}</p>
            <TagList tags={result.skill.tag_names} />
          </article>
        ))}
      </div>
    </section>
  );
}

function RequestCard({ skill, myOfferedSkills, onCreateRequest }) {
  const [message, setMessage] = useState("");
  const [offeredSkillId, setOfferedSkillId] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    await onCreateRequest({
      requested_skill_id: skill.id,
      offered_skill_id: offeredSkillId ? Number(offeredSkillId) : undefined,
      message,
    });
    setMessage("");
    setOfferedSkillId("");
  }

  return (
    <article className="item-card">
      <div className="item-header">
        <strong>{skill.title}</strong>
        <span className="pill pill-offer">{skill.category}</span>
      </div>
      <p>{skill.description}</p>
      {skill.ai_summary ? <p className="meta-block">{skill.ai_summary}</p> : null}
      <TagList tags={skill.tag_names} />
      <p className="meta-line">
        {skill.owner.name}
        {skill.owner.city ? ` • ${skill.owner.city}` : ""}
        {skill.availability ? ` • ${skill.availability}` : ""}
      </p>
      <form className="stack compact-form" onSubmit={handleSubmit}>
        <label>
          Offer one of your skills
          <select value={offeredSkillId} onChange={(event) => setOfferedSkillId(event.target.value)}>
            <option value="">Optional</option>
            {myOfferedSkills.map((offeredSkill) => (
              <option key={offeredSkill.id} value={offeredSkill.id}>
                {offeredSkill.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          Message
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            rows="3"
            placeholder="Leave blank to let the system draft an intro message."
          />
        </label>
        <button className="primary-button" type="submit">
          Send request
        </button>
      </form>
    </article>
  );
}

function SkillsPanel({
  mySkills,
  allSkills,
  currentUser,
  onCreateSkill,
  onDeleteSkill,
  onAssistSkill,
  loading,
  assisting,
  onCreateRequest,
}) {
  const offeredSkills = useMemo(
    () => mySkills.filter((skill) => skill.skill_type === "offer"),
    [mySkills],
  );
  const requestableSkills = useMemo(
    () =>
      allSkills.filter(
        (skill) => skill.user_id !== currentUser.id && skill.skill_type === "offer",
      ),
    [allSkills, currentUser.id],
  );

  return (
    <section className="panel panel-wide">
      <div className="panel-heading">
        <h2>Skills</h2>
        <p>Create listings with AI assistance, automatic tags, and richer descriptions.</p>
      </div>

      <div className="dual-grid">
        <div className="subpanel">
          <h3>Create a skill</h3>
          <SkillForm
            onSubmit={onCreateSkill}
            onAssist={onAssistSkill}
            loading={loading}
            assisting={assisting}
          />
        </div>

        <div className="subpanel">
          <h3>Your skills</h3>
          <div className="card-list">
            {mySkills.length === 0 ? <p className="empty-state">No skills yet.</p> : null}
            {mySkills.map((skill) => (
              <article className="item-card" key={skill.id}>
                <div className="item-header">
                  <strong>{skill.title}</strong>
                  <span className={`pill pill-${skill.skill_type}`}>{skill.skill_type}</span>
                </div>
                <p>{skill.description}</p>
                {skill.ai_summary ? <p className="meta-block">{skill.ai_summary}</p> : null}
                <p className="meta-line">
                  {skill.category}
                  {skill.proficiency_level ? ` • ${skill.proficiency_level}` : ""}
                  {skill.availability ? ` • ${skill.availability}` : ""}
                </p>
                <TagList tags={skill.tag_names} />
                <button
                  className="ghost-button"
                  type="button"
                  onClick={() => onDeleteSkill(skill.id)}
                >
                  Delete
                </button>
              </article>
            ))}
          </div>
        </div>
      </div>

      <div className="subpanel">
        <h3>Available offers</h3>
        <div className="card-list">
          {requestableSkills.length === 0 ? (
            <p className="empty-state">No public offers from other users yet.</p>
          ) : null}
          {requestableSkills.map((skill) => (
            <RequestCard
              key={skill.id}
              skill={skill}
              myOfferedSkills={offeredSkills}
              onCreateRequest={onCreateRequest}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

function MatchesPanel({ matches }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Semantic matches</h2>
        <p>These suggestions use semantic overlap, categories, and auto-generated tags.</p>
      </div>
      <div className="card-list">
        {matches.length === 0 ? (
          <p className="empty-state">No semantic matches yet. Add more request skills to widen coverage.</p>
        ) : null}
        {matches.map((match) => (
          <article
            className="item-card item-card-accent"
            key={`${match.current_user_skill.id}-${match.matching_skill.id}`}
          >
            <div className="item-header">
              <strong>{match.matching_skill.title}</strong>
              <span className="pill pill-offer">score {Math.round(match.match_score * 100)}%</span>
            </div>
            <p className="match-label">Your request</p>
            <p>{match.current_user_skill.title}</p>
            <p className="match-label">Suggested offer</p>
            <p>
              {match.matching_skill.owner.name}
              {match.matching_skill.owner.city ? ` • ${match.matching_skill.owner.city}` : ""}
            </p>
            <p>{match.matching_skill.description}</p>
            <p className="helper-text">{match.rationale}</p>
            <TagList tags={match.shared_tags} />
          </article>
        ))}
      </div>
    </section>
  );
}

function RequestsPanel({ requests, currentUser, onStatusChange, onOpenChat }) {
  function getActions(exchangeRequest) {
    const actions = [];
    const isRecipient = exchangeRequest.recipient_id === currentUser.id;
    const isRequester = exchangeRequest.requester_id === currentUser.id;

    if (exchangeRequest.status === "pending") {
      if (isRecipient) {
        actions.push({ label: "Accept", status: "accepted" });
        actions.push({ label: "Reject", status: "rejected" });
      }

      if (isRequester) {
        actions.push({ label: "Cancel", status: "cancelled" });
      }
    }

    if (exchangeRequest.status === "accepted") {
      if (isRequester) {
        actions.push({ label: "Complete", status: "completed" });
      }
      actions.push({ label: "Open chat", chat: true });
    }

    return actions;
  }

  return (
    <section className="panel panel-wide">
      <div className="panel-heading">
        <h2>Exchange requests</h2>
        <p>Accepted requests can open a direct chat thread between tutor and mentee.</p>
      </div>
      <div className="card-list">
        {requests.length === 0 ? <p className="empty-state">No requests yet.</p> : null}
        {requests.map((exchangeRequest) => (
          <article className="item-card" key={exchangeRequest.id}>
            <div className="item-header">
              <strong>{exchangeRequest.requested_skill.title}</strong>
              <span className={`pill pill-${exchangeRequest.status}`}>
                {exchangeRequest.status}
              </span>
            </div>
            <p>
              Requester: {exchangeRequest.requester.name} | Recipient: {exchangeRequest.recipient.name}
            </p>
            {exchangeRequest.offered_skill ? (
              <p>Offered back: {exchangeRequest.offered_skill.title}</p>
            ) : null}
            {exchangeRequest.message ? <p>{exchangeRequest.message}</p> : null}
            <div className="inline-actions">
              {getActions(exchangeRequest).map((action) =>
                action.chat ? (
                  <button
                    className="ghost-button"
                    key={`chat-${exchangeRequest.id}`}
                    type="button"
                    onClick={() => onOpenChat(exchangeRequest.id)}
                  >
                    {action.label}
                  </button>
                ) : (
                  <button
                    className="ghost-button"
                    key={action.status}
                    type="button"
                    onClick={() => onStatusChange(exchangeRequest.id, action.status)}
                  >
                    {action.label}
                  </button>
                ),
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function ChatPanel({ threads, activeThread, currentUser, onOpenThread, onSendMessage, sending }) {
  const [message, setMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!activeThread || !message.trim()) {
      return;
    }
    await onSendMessage(activeThread.id, message);
    setMessage("");
  }

  return (
    <section className="panel panel-wide">
      <div className="panel-heading">
        <h2>Chat</h2>
        <p>Private discussion is available once an exchange request has been accepted.</p>
      </div>
      <div className="chat-layout">
        <div className="subpanel">
          <h3>Threads</h3>
          <div className="card-list">
            {threads.length === 0 ? (
              <p className="empty-state">No chat threads yet.</p>
            ) : null}
            {threads.map((thread) => (
              <button
                className={`thread-card ${activeThread?.id === thread.id ? "thread-card-active" : ""}`}
                key={thread.id}
                type="button"
                onClick={() => onOpenThread(thread.id)}
              >
                <strong>{thread.exchange_request.requested_skill.title}</strong>
                <span className="helper-text">
                  {thread.exchange_request.requester_id === currentUser.id
                    ? thread.exchange_request.recipient.name
                    : thread.exchange_request.requester.name}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="subpanel">
          {activeThread ? (
            <>
              <h3>{activeThread.exchange_request.requested_skill.title}</h3>
              <div className="message-list">
                {activeThread.messages.map((chatMessage) => (
                  <article
                    className={`message-bubble ${
                      chatMessage.sender_id === currentUser.id ? "message-own" : ""
                    }`}
                    key={chatMessage.id}
                  >
                    <strong>{chatMessage.sender.name}</strong>
                    <p>{chatMessage.content}</p>
                  </article>
                ))}
              </div>
              <form className="chat-compose" onSubmit={handleSubmit}>
                <textarea
                  rows="3"
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="Send a message"
                />
                <button className="primary-button" type="submit" disabled={sending}>
                  {sending ? "Sending..." : "Send"}
                </button>
              </form>
            </>
          ) : (
            <p className="empty-state">Open an accepted request to start chatting.</p>
          )}
        </div>
      </div>
    </section>
  );
}

function App() {
  const [authMode, setAuthMode] = useState("signup");
  const [token, setToken] = useState(() => localStorage.getItem("skill_exchange_token") || "");
  const [profile, setProfile] = useState(null);
  const [allSkills, setAllSkills] = useState([]);
  const [mySkills, setMySkills] = useState([]);
  const [matches, setMatches] = useState([]);
  const [requests, setRequests] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [chatThreads, setChatThreads] = useState([]);
  const [activeThread, setActiveThread] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [loadingSkillCreate, setLoadingSkillCreate] = useState(false);
  const [loadingSkillAssist, setLoadingSkillAssist] = useState(false);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [authError, setAuthError] = useState("");
  const [appError, setAppError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!token) {
      setProfile(null);
      setAllSkills([]);
      setMySkills([]);
      setMatches([]);
      setRequests([]);
      setChatThreads([]);
      setActiveThread(null);
      return;
    }

    async function loadDashboard() {
      try {
        setAppError("");
        const [profileData, allSkillsData, mySkillsData, matchesData, requestsData, threadsData] =
          await Promise.all([
            api.getProfile(token),
            api.listSkills(token),
            api.listMySkills(token),
            api.getMatches(token),
            api.listExchangeRequests(token),
            api.listChatThreads(token),
          ]);

        setProfile(profileData);
        setAllSkills(allSkillsData);
        setMySkills(mySkillsData);
        setMatches(matchesData);
        setRequests(requestsData);
        setChatThreads(threadsData);
        if (activeThread) {
          const refreshedThread = threadsData.find((thread) => thread.id === activeThread.id);
          setActiveThread(refreshedThread || null);
        }
      } catch (error) {
        setAppError(error.message);
        if (String(error.message).toLowerCase().includes("token")) {
          handleLogout();
        }
      }
    }

    loadDashboard();
  }, [token, refreshKey]);

  function handleLogout() {
    localStorage.removeItem("skill_exchange_token");
    setToken("");
  }

  async function handleAuthSubmit(form) {
    setLoadingAuth(true);
    setAuthError("");

    try {
      if (authMode === "signup") {
        await api.signup(toPayload(form));
      }

      const loginResponse = await api.login({
        email: form.email,
        password: form.password,
      });
      localStorage.setItem("skill_exchange_token", loginResponse.access_token);
      setToken(loginResponse.access_token);
      setAuthMode("login");
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setLoadingAuth(false);
    }
  }

  async function handleProfileSave(form) {
    setLoadingProfile(true);
    setAppError("");
    try {
      const updatedProfile = await api.updateProfile(token, toPayload(form));
      setProfile(updatedProfile);
    } catch (error) {
      setAppError(error.message);
    } finally {
      setLoadingProfile(false);
    }
  }

  async function handleAssistSkill(form) {
    setLoadingSkillAssist(true);
    setAppError("");
    try {
      return await api.suggestSkill(toPayload(form));
    } catch (error) {
      setAppError(error.message);
      return null;
    } finally {
      setLoadingSkillAssist(false);
    }
  }

  async function handleCreateSkill(form, reset) {
    setLoadingSkillCreate(true);
    setAppError("");
    try {
      await api.createSkill(token, toPayload(form));
      reset();
      setRefreshKey((current) => current + 1);
    } catch (error) {
      setAppError(error.message);
    } finally {
      setLoadingSkillCreate(false);
    }
  }

  async function handleDeleteSkill(skillId) {
    try {
      await api.deleteSkill(token, skillId);
      setRefreshKey((current) => current + 1);
    } catch (error) {
      setAppError(error.message);
    }
  }

  async function handleSearch(query) {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    setLoadingSearch(true);
    setAppError("");
    try {
      const results = await api.searchSkills(token, query);
      setSearchResults(results);
    } catch (error) {
      setAppError(error.message);
    } finally {
      setLoadingSearch(false);
    }
  }

  async function handleCreateRequest(payload) {
    try {
      await api.createExchangeRequest(token, payload);
      setRefreshKey((current) => current + 1);
    } catch (error) {
      setAppError(error.message);
    }
  }

  async function handleRequestStatusChange(requestId, status) {
    try {
      await api.updateExchangeRequestStatus(token, requestId, { status });
      setRefreshKey((current) => current + 1);
    } catch (error) {
      setAppError(error.message);
    }
  }

  async function handleOpenChat(exchangeRequestId) {
    try {
      const thread = await api.createChatThread(token, exchangeRequestId);
      setActiveThread(thread);
      setRefreshKey((current) => current + 1);
    } catch (error) {
      setAppError(error.message);
    }
  }

  async function handleOpenThread(threadId) {
    try {
      const thread = await api.getChatThread(token, threadId);
      setActiveThread(thread);
    } catch (error) {
      setAppError(error.message);
    }
  }

  async function handleSendMessage(threadId, content) {
    setSendingMessage(true);
    setAppError("");
    try {
      await api.sendChatMessage(token, threadId, { content });
      const thread = await api.getChatThread(token, threadId);
      setActiveThread(thread);
      setRefreshKey((current) => current + 1);
    } catch (error) {
      setAppError(error.message);
    } finally {
      setSendingMessage(false);
    }
  }

  if (!token || !profile) {
    return (
      <main className="page-shell">
        <AuthForm
          mode={authMode}
          onModeChange={setAuthMode}
          onSubmit={handleAuthSubmit}
          loading={loadingAuth}
          error={authError}
        />
      </main>
    );
  }

  return (
    <main className="page-shell">
      <section className="dashboard-header">
        <div>
          <p className="eyebrow">Skill Exchange Platform</p>
          <h1>{profile.name}&apos;s dashboard</h1>
          <p className="hero-copy">
            Publish skill supply and demand, review semantic matches, search naturally, and
            chat after requests are accepted.
          </p>
        </div>
        <button className="ghost-button" type="button" onClick={handleLogout}>
          Logout
        </button>
      </section>

      {appError ? <p className="global-error">{appError}</p> : null}

      <div className="dashboard-grid">
        <ProfilePanel profile={profile} onSave={handleProfileSave} loading={loadingProfile} />
        <MatchesPanel matches={matches} />
      </div>

      <SearchPanel results={searchResults} loading={loadingSearch} onSearch={handleSearch} />

      <SkillsPanel
        mySkills={mySkills}
        allSkills={allSkills}
        currentUser={profile}
        onCreateSkill={handleCreateSkill}
        onDeleteSkill={handleDeleteSkill}
        onAssistSkill={handleAssistSkill}
        loading={loadingSkillCreate}
        assisting={loadingSkillAssist}
        onCreateRequest={handleCreateRequest}
      />

      <RequestsPanel
        requests={requests}
        currentUser={profile}
        onStatusChange={handleRequestStatusChange}
        onOpenChat={handleOpenChat}
      />

      <ChatPanel
        threads={chatThreads}
        activeThread={activeThread}
        currentUser={profile}
        onOpenThread={handleOpenThread}
        onSendMessage={handleSendMessage}
        sending={sendingMessage}
      />
    </main>
  );
}

export default App;
