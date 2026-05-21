import { useState } from "react";
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

const recommendedProblems = [
  {
    id: 1,
    title: "Two Sum",
    difficulty: "Easy",
    tags: ["Array", "Hashing"],
    reason:
      "Best mixed revision problem because it refreshes Array traversal while strengthening Hash Map lookup.",
    link: "https://leetcode.com/problems/two-sum/",
    statement:
      "Given an array of integers and a target value, return the indices of two numbers such that they add up to the target.",
    sample: "nums = [2, 7, 11, 15], target = 9 → [0, 1]",
    code: `function twoSum(nums, target) {
  const seen = new Map();

  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];

    if (seen.has(need)) {
      return [seen.get(need), i];
    }

    seen.set(nums[i], i);
  }
}`,
    review: {
      clarity: "Good",
      pattern: "Hash Map Lookup",
      time: "O(n)",
      space: "O(n)",
      edge: "Duplicate values",
      note:
        "Your logic is optimized. Next, solve one variation where the array contains repeated numbers to check whether your hashing concept is stable.",
    },
  },
  {
    id: 2,
    title: "Contains Duplicate",
    difficulty: "Easy",
    tags: ["Array", "Set"],
    reason:
      "Good quick recall problem for Arrays and introduces HashSet based duplicate detection.",
    link: "https://leetcode.com/problems/contains-duplicate/",
    statement:
      "Given an integer array, return true if any value appears at least twice, and return false if every element is distinct.",
    sample: "nums = [1, 2, 3, 1] → true",
    code: `function containsDuplicate(nums) {
  const seen = new Set();

  for (const num of nums) {
    if (seen.has(num)) {
      return true;
    }

    seen.add(num);
  }

  return false;
}`,
    review: {
      clarity: "Strong",
      pattern: "HashSet Tracking",
      time: "O(n)",
      space: "O(n)",
      edge: "Empty array",
      note:
        "This is a strong recall problem. It checks whether you remember array traversal and can apply set-based duplicate detection cleanly.",
    },
  },
  {
    id: 3,
    title: "Subarray Sum Equals K",
    difficulty: "Medium",
    tags: ["Prefix Sum", "Hashing"],
    reason:
      "Recommended because Prefix Sum is marked weak and this problem connects it with Hashing.",
    link: "https://leetcode.com/problems/subarray-sum-equals-k/",
    statement:
      "Given an array of integers and an integer k, return the total number of continuous subarrays whose sum equals k.",
    sample: "nums = [1, 1, 1], k = 2 → 2",
    code: `function subarraySum(nums, k) {
  const prefixCount = new Map();
  prefixCount.set(0, 1);

  let sum = 0;
  let count = 0;

  for (const num of nums) {
    sum += num;

    if (prefixCount.has(sum - k)) {
      count += prefixCount.get(sum - k);
    }

    prefixCount.set(sum, (prefixCount.get(sum) || 0) + 1);
  }

  return count;
}`,
    review: {
      clarity: "Needs Revision",
      pattern: "Prefix Sum + Hash Map",
      time: "O(n)",
      space: "O(n)",
      edge: "Negative numbers",
      note:
        "This problem is important because normal sliding window may fail with negative numbers. Prefix sum with hash map is the correct pattern to revise.",
    },
  },
];

function getStatusClass(status) {
  if (status === "Active") return "node-active";
  if (status === "Revision Due") return "node-danger";
  if (status === "Fading") return "node-warning";
  return "node-muted";
}

function App() {
  const [selectedProblem, setSelectedProblem] = useState(recommendedProblems[0]);
  const [userCode, setUserCode] = useState(recommendedProblems[0].code);
  const [reviewGenerated, setReviewGenerated] = useState(false);

  function handlePracticeHere(problem) {
    setSelectedProblem(problem);
    setUserCode(problem.code);
    setReviewGenerated(false);
  }

  function handleReviewCode() {
    setReviewGenerated(true);
  }

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
            <button onClick={handleReviewCode}>Review Code</button>
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

      <section className="recommend-panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Recommended Problem Bank</p>
            <h2>What should you solve next?</h2>
          </div>
          <span className="live-pill">Selected by Recall Engine</span>
        </div>

        <div className="problem-grid">
          {recommendedProblems.map((problem) => (
            <article
              className={`recommend-card ${selectedProblem.id === problem.id ? "selected-problem" : ""
                }`}
              key={problem.title}
            >
              <div className="recommend-top">
                <div>
                  <span className="difficulty-pill">{problem.difficulty}</span>
                  <h3>{problem.title}</h3>
                </div>
                <span className="match-score">92% Match</span>
              </div>

              <div className="tag-row">
                {problem.tags.map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>

              <p>{problem.reason}</p>

              <div className="recommend-actions">
                <a href={problem.link} target="_blank" rel="noreferrer">
                  Open on LeetCode
                </a>
                <button onClick={() => handlePracticeHere(problem)}>
                  Practice Here
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="workspace-panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Practice Workspace</p>
            <h2>{selectedProblem.title} · AI Solving Companion</h2>
          </div>
          <span className="live-pill">Editable Code Review</span>
        </div>

        <div className="workspace-grid">
          <div className="problem-card">
            <div className="problem-top">
              <div>
                <span className="difficulty-pill">
                  {selectedProblem.difficulty}
                </span>
                <h3>{selectedProblem.title}</h3>
              </div>
              <span className="topic-tag">
                {selectedProblem.tags.join(" + ")}
              </span>
            </div>

            <p>{selectedProblem.statement}</p>

            <div className="problem-detail">
              <span>Why this problem?</span>
              <p>{selectedProblem.reason}</p>
            </div>

            <div className="test-box">
              <span>Sample</span>
              <code>{selectedProblem.sample}</code>
            </div>
          </div>

          <div className="code-card editable-code-card">
            <div className="code-head">
              <span>Paste / Edit Your Code</span>
              <strong>JavaScript</strong>
            </div>

            <textarea
              className="code-editor"
              value={userCode}
              onChange={(event) => {
                setUserCode(event.target.value);
                setReviewGenerated(false);
              }}
              spellCheck="false"
            />

            <div className="code-actions">
              <button onClick={handleReviewCode}>Review Code</button>
              <button
                onClick={() => {
                  setUserCode(selectedProblem.code);
                  setReviewGenerated(false);
                }}
              >
                Reset Sample
              </button>
            </div>
          </div>

          <div className={`review-card ${reviewGenerated ? "review-ready" : ""}`}>
            <p className="eyebrow">AI Review Preview</p>
            <h3>
              {reviewGenerated
                ? `Review generated: ${selectedProblem.review.clarity}`
                : "Waiting for code review"}
            </h3>

            {!reviewGenerated && (
              <div className="empty-review">
                <span>Paste your solution</span>
                <p>
                  Click Review Code to simulate how the AI mentor will analyze
                  pattern, complexity, edge cases, and revision needs.
                </p>
              </div>
            )}

            {reviewGenerated && (
              <>
                <div className="review-list">
                  <div>
                    <span>Pattern detected</span>
                    <strong>{selectedProblem.review.pattern}</strong>
                  </div>

                  <div>
                    <span>Time complexity</span>
                    <strong>{selectedProblem.review.time}</strong>
                  </div>

                  <div>
                    <span>Space complexity</span>
                    <strong>{selectedProblem.review.space}</strong>
                  </div>

                  <div>
                    <span>Edge case to revise</span>
                    <strong>{selectedProblem.review.edge}</strong>
                  </div>
                </div>

                <div className="ai-note">
                  <span>AI Mentor Note</span>
                  <p>{selectedProblem.review.note}</p>
                </div>

                <button className="secondary-btn">
                  Add Similar Problem to Revision
                </button>
              </>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

export default App;