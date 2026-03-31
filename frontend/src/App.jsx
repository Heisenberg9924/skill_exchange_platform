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
    Object.entries(values).filter(([, value]) => value !== ""),
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
        <p className="eyebrow">Production-ready MVP</p>
        <h1>Trade practical skills with people who can help right now.</h1>
        <p className="hero-copy">
          Manage your profile, publish what you can teach or need, discover relevant
          matches, and send structured exchange requests from one dashboard.
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
          {loading
            ? "Submitting..."
            : mode === "signup"
              ? "Create account"
              : "Sign in"}
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

  async function handleSubmit(event) {
    event.preventDefault();
    await onSave(form);
    setMessage("Profile updated.");
  }

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    if (message) {
      setMessage("");
    }
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Profile</h2>
        <p>Keep your public details current so potential matches know how to reach you.</p>
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

function SkillForm({ onSubmit, loading, initialValues = emptySkillForm, submitLabel = "Add skill" }) {
  const [form, setForm] = useState(initialValues);

  useEffect(() => {
    setForm(initialValues);
  }, [initialValues]);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await onSubmit(form, () => setForm(emptySkillForm));
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
      <button className="primary-button" type="submit" disabled={loading}>
        {loading ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}

function SkillsPanel({
  mySkills,
  allSkills,
  currentUser,
  onCreateSkill,
  onDeleteSkill,
  loading,
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
        <p>Create what you can offer and what you need so the matching engine has signal.</p>
      </div>

      <div className="dual-grid">
        <div className="subpanel">
          <h3>Create a skill</h3>
          <SkillForm onSubmit={onCreateSkill} loading={loading} />
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
                <p className="meta-line">
                  {skill.category}
                  {skill.proficiency_level ? ` • ${skill.proficiency_level}` : ""}
                  {skill.availability ? ` • ${skill.availability}` : ""}
                </p>
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
          <textarea value={message} onChange={(event) => setMessage(event.target.value)} rows="3" />
        </label>
        <button className="primary-button" type="submit">
          Send request
        </button>
      </form>
    </article>
  );
}

function MatchesPanel({ matches }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Matches</h2>
        <p>Automatic suggestions based on your requested skills and other users&apos; offers.</p>
      </div>
      <div className="card-list">
        {matches.length === 0 ? (
          <p className="empty-state">No direct matches yet. Add more request skills to widen coverage.</p>
        ) : null}
        {matches.map((match) => (
          <article
            className="item-card item-card-accent"
            key={`${match.current_user_skill.id}-${match.matching_skill.id}`}
          >
            <p className="match-label">Your request</p>
            <strong>{match.current_user_skill.title}</strong>
            <p>{match.current_user_skill.description}</p>
            <p className="match-label">Matching offer</p>
            <strong>{match.matching_skill.title}</strong>
            <p>{match.matching_skill.owner.name}</p>
            <p>{match.matching_skill.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function RequestsPanel({ requests, currentUser, onStatusChange }) {
  function getActions(exchangeRequest) {
    const actions = [];
    const isRecipient = exchangeRequest.recipient_id === currentUser.id;
    const isRequester = exchangeRequest.requester_id === currentUser.id;

    if (exchangeRequest.status !== "pending") {
      return actions;
    }

    if (isRecipient) {
      actions.push({ label: "Accept", status: "accepted" });
      actions.push({ label: "Reject", status: "rejected" });
    }

    if (isRequester) {
      actions.push({ label: "Cancel", status: "cancelled" });
    }

    return actions;
  }

  return (
    <section className="panel panel-wide">
      <div className="panel-heading">
        <h2>Exchange requests</h2>
        <p>Track inbound and outbound requests and update lifecycle status from one place.</p>
      </div>
      <div className="card-list">
        {requests.length === 0 ? (
          <p className="empty-state">No requests yet.</p>
        ) : null}
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
              {getActions(exchangeRequest).map((action) => (
                <button
                  className="ghost-button"
                  key={action.status}
                  type="button"
                  onClick={() => onStatusChange(exchangeRequest.id, action.status)}
                >
                  {action.label}
                </button>
              ))}
            </div>
          </article>
        ))}
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
  const [loadingAuth, setLoadingAuth] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [loadingSkillCreate, setLoadingSkillCreate] = useState(false);
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
      return;
    }

    async function loadDashboard() {
      try {
        setAppError("");
        const [profileData, allSkillsData, mySkillsData, matchesData, requestsData] =
          await Promise.all([
            api.getProfile(token),
            api.listSkills(token),
            api.listMySkills(token),
            api.getMatches(token),
            api.listExchangeRequests(token),
          ]);

        setProfile(profileData);
        setAllSkills(allSkillsData);
        setMySkills(mySkillsData);
        setMatches(matchesData);
        setRequests(requestsData);
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
            Publish skill supply and demand, review request flow, and act on suggested matches.
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

      <SkillsPanel
        mySkills={mySkills}
        allSkills={allSkills}
        currentUser={profile}
        onCreateSkill={handleCreateSkill}
        onDeleteSkill={handleDeleteSkill}
        loading={loadingSkillCreate}
        onCreateRequest={handleCreateRequest}
      />

      <RequestsPanel
        requests={requests}
        currentUser={profile}
        onStatusChange={handleRequestStatusChange}
      />
    </main>
  );
}

export default App;
