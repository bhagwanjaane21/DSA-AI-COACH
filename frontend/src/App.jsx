import "./App.css";

const topics = [
  {
    name: "Arrays",
    status: "Revision Due",
    mastery: 74,
    daysAgo: 8,
    risk: 64,
    position: "node-pos-1",
  },
  {
    name: "Hashing",
    status: "Active",
    mastery: 61,
    daysAgo: 1,
    risk: 10,
    position: "node-pos-2",
  },
  {
    name: "Sliding Window",
    status: "Upcoming",
    mastery: 20,
    daysAgo: 0,
    risk: 0,
    position: "node-pos-3",
  },
  {
    name: "Binary Search",
    status: "Fading",
    mastery: 48,
    daysAgo: 5,
    risk: 35,
    position: "node-pos-4",
  },
];

const todayPlan = [
  "Revise one Array problem to refresh old memory.",
  "Practice two Hashing problems based on frequency maps.",
  "Solve one mixed Array + Hashing problem.",
];

function getStatusClass(status) {
  if (status === "Active") return "node-active";
  if (status === "Revision Due") return "node-danger";
  if (status === "Fading") return "node-warning";
  return "node-muted";
}

function App() {
  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">AI + Spaced Revision for DSA</p>
          <h1>AlgoMentor AI</h1>
          <p className="subtitle">
            A neural recall dashboard that reminds students what to revise
            before old DSA concepts fade away.
          </p>
        </div>

        <div className="hero-badge">
          <span>Today</span>
          <strong>Arrays revision is due</strong>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Current Topic</span>
          <strong>Hashing</strong>
          <p>Learning for 5 days</p>
        </div>

        <div className="stat-card danger">
          <span>Highest Forgetting Risk</span>
          <strong>Arrays · 64%</strong>
          <p>Last practiced 8 days ago</p>
        </div>

        <div className="stat-card">
          <span>Consistency Score</span>
          <strong>72%</strong>
          <p>4 active days this week</p>
        </div>

        <div className="stat-card">
          <span>Revision Queue</span>
          <strong>3 Topics</strong>
          <p>Arrays, Binary Search, Prefix Sum</p>
        </div>
      </section>

      <section className="main-grid">
        <div className="memory-card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Memory Map</p>
              <h2>DSA Topic Recall Network</h2>
            </div>
            <span className="live-pill">Live Risk Scan</span>
          </div>

          <div className="memory-map">
            <div className="connection c1" />
            <div className="connection c2" />
            <div className="connection c3" />

            {topics.map((topic) => (
              <div
                key={topic.name}
                className={`topic-node ${topic.position} ${getStatusClass(
                  topic.status
                )}`}
              >
                <span>{topic.name}</span>
                <small>{topic.status}</small>

                <div className="mini-bar">
                  <div style={{ width: `${topic.mastery}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <aside className="mentor-panel">
          <p className="eyebrow">AI Mentor</p>
          <h2>Why revise Arrays today?</h2>

          <p>
            You are currently learning Hashing, but Arrays was last practiced 8
            days ago. Since Hashing problems often combine array traversal with
            frequency maps, revising Arrays now will strengthen your current
            topic too.
          </p>

          <div className="decay-meter">
            <div className="decay-top">
              <span>Memory Decay</span>
              <strong>64%</strong>
            </div>

            <div className="decay-track">
              <div className="decay-fill" />
            </div>

            <p>
              Arrays has entered the revision zone. A quick recall task today
              can prevent concept fading.
            </p>
          </div>

          <div className="mentor-insight">
            <span>Recommendation</span>
            <strong>Solve 1 Array recall + 1 Array-Hashing mixed problem</strong>
          </div>

          <div className="mentor-actions">
            <button>Analyze Pattern</button>
            <button>Review Code</button>
            <button>Schedule Revision</button>
            <button>Next Problem</button>
          </div>

          <button className="primary-btn">Generate Today’s Practice</button>
        </aside>
      </section>

      <section className="bottom-grid">
        <div className="plan-card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Smart Plan</p>
              <h2>Today’s DSA Tasks</h2>
            </div>
          </div>

          <div className="task-list">
            {todayPlan.map((task, index) => (
              <div className="task-item" key={task}>
                <span>0{index + 1}</span>
                <p>{task}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="queue-card">
          <p className="eyebrow">Revision Queue</p>
          <h2>Concepts close to fading</h2>

          <div className="queue-item">
            <span>Arrays</span>
            <strong>64% Risk</strong>
          </div>

          <div className="queue-item">
            <span>Binary Search</span>
            <strong>35% Risk</strong>
          </div>

          <div className="queue-item">
            <span>Prefix Sum</span>
            <strong>28% Risk</strong>
          </div>
        </div>
      </section>
    </main>
  );
}

export default App;