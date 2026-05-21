-- ============================================================
-- AI DSA Coach — PostgreSQL Schema (Supabase)
-- Run this in your Supabase SQL Editor to create all tables.
-- ============================================================

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    current_level VARCHAR(50) DEFAULT 'Beginner',
    weak_topics TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Problems table
CREATE TABLE IF NOT EXISTS problems (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Schedules table
CREATE TABLE IF NOT EXISTS schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    classes_schedule TEXT,
    free_hours INT DEFAULT 0,
    weekly_plan JSONB DEFAULT '[]'::jsonb,
    overall_focus TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Submissions table (structured metadata, not just raw code)
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    optimization_score FLOAT NOT NULL,
    edge_case_score FLOAT NOT NULL,
    pattern_understanding_score FLOAT NOT NULL,
    feedback TEXT,
    time_complexity VARCHAR(50),
    space_complexity VARCHAR(50),
    hints_used INT DEFAULT 0,
    time_taken INT DEFAULT 0,
    weak_topic VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Revision queue with SM-2 spaced repetition state
CREATE TABLE IF NOT EXISTS revision_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    topic VARCHAR(100) NOT NULL,
    scheduled_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    reasoning TEXT,
    repetition INT DEFAULT 0,
    easiness_factor FLOAT DEFAULT 2.5,
    interval_days INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_problem_revision UNIQUE (user_id, problem_id)
);

-- 6. Learning insights (aggregated trends and revision history)
CREATE TABLE IF NOT EXISTS learning_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    weak_topics TEXT[] DEFAULT '{}',
    improvement_trends JSONB DEFAULT '{}'::jsonb,
    revision_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Indexes for query performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_problem ON submissions(problem_id);
CREATE INDEX IF NOT EXISTS idx_submissions_created ON submissions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_revision_user_status ON revision_queue(user_id, status);
CREATE INDEX IF NOT EXISTS idx_revision_scheduled ON revision_queue(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_schedules_user ON schedules(user_id);
CREATE INDEX IF NOT EXISTS idx_problems_topic ON problems(topic);

-- ============================================================
-- Seed: Sample DSA problems
-- ============================================================
INSERT INTO problems (id, title, difficulty, topic, description) VALUES
    ('two-sum', 'Two Sum', 'Easy', 'Arrays', 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.'),
    ('reverse-linked-list', 'Reverse Linked List', 'Easy', 'Linked List', 'Given the head of a singly linked list, reverse the list, and return the reversed list.'),
    ('valid-parentheses', 'Valid Parentheses', 'Easy', 'Stack', 'Given a string s containing just the characters ''('', '')'', ''{'', ''}'', ''['' and '']'', determine if the input string is valid.'),
    ('binary-search', 'Binary Search', 'Easy', 'Binary Search', 'Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums.'),
    ('climbing-stairs', 'Climbing Stairs', 'Easy', 'Dynamic Programming', 'You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?'),
    ('best-time-to-buy-sell', 'Best Time to Buy and Sell Stock', 'Easy', 'Arrays', 'You are given an array prices where prices[i] is the price of a given stock on the ith day. Maximize profit by choosing a single day to buy and a single day to sell.'),
    ('merge-two-sorted-lists', 'Merge Two Sorted Lists', 'Easy', 'Linked List', 'You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list.'),
    ('maximum-subarray', 'Maximum Subarray', 'Medium', 'Arrays', 'Given an integer array nums, find the subarray with the largest sum, and return its sum.'),
    ('3sum', 'Three Sum', 'Medium', 'Arrays', 'Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.'),
    ('longest-substring-no-repeat', 'Longest Substring Without Repeating Characters', 'Medium', 'String', 'Given a string s, find the length of the longest substring without repeating characters.'),
    ('coin-change', 'Coin Change', 'Medium', 'Dynamic Programming', 'You are given an integer array coins representing coins of different denominations and an integer amount. Return the fewest number of coins needed to make up that amount.'),
    ('lru-cache', 'LRU Cache', 'Medium', 'Design', 'Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.'),
    ('number-of-islands', 'Number of Islands', 'Medium', 'Graph', 'Given an m x n 2D binary grid which represents a map of ''1''s (land) and ''0''s (water), return the number of islands.'),
    ('word-break', 'Word Break', 'Medium', 'Dynamic Programming', 'Given a string s and a dictionary of strings wordDict, return true if s can be segmented into a space-separated sequence of one or more dictionary words.'),
    ('merge-intervals', 'Merge Intervals', 'Medium', 'Arrays', 'Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals.'),
    ('trapping-rain-water', 'Trapping Rain Water', 'Hard', 'Arrays', 'Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.'),
    ('median-two-sorted-arrays', 'Median of Two Sorted Arrays', 'Hard', 'Binary Search', 'Given two sorted arrays nums1 and nums2, return the median of the two sorted arrays. The overall run time complexity should be O(log (m+n)).'),
    ('serialize-deserialize-tree', 'Serialize and Deserialize Binary Tree', 'Hard', 'Trees', 'Design an algorithm to serialize and deserialize a binary tree.'),
    ('minimum-window-substring', 'Minimum Window Substring', 'Hard', 'String', 'Given two strings s and t, return the minimum window substring of s such that every character in t is included in the window.'),
    ('alien-dictionary', 'Alien Dictionary', 'Hard', 'Graph', 'Given a sorted dictionary of an alien language, find the order of characters in the alien language.')
ON CONFLICT (id) DO NOTHING;
