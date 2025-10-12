import { test, expect } from '@playwright/test';

// Test data
const TEACHER = {
  username: 'teacher1',
  password: 'password123'
};

const STUDENT = {
  username: 'student1',
  password: 'password123'
};

const TEST_POLL = {
  question: 'Playwright Test Poll',
  options: ['Option A', 'Option B', 'Option C'],
  courseId: 'COMP5241'
};

test.describe('Poll System Frontend', () => {
  test.beforeEach(async ({ page }) => {
    // Start from the polls page
    await page.goto('/polls');
    
    // Verify we're on the polls page
    await expect(page).toHaveTitle(/Interactive Poll System/);
    await expect(page.locator('h1')).toContainText('Interactive Poll System');
  });

  test('Login as teacher', async ({ page }) => {
    // Fill login form
    await page.locator('#username').fill(TEACHER.username);
    await page.locator('#password').fill(TEACHER.password);
    await page.locator('#isTeacher').check();
    await page.locator('button:has-text("Login")').click();
    
    // Verify successful login
    await expect(page.locator('#userDisplay')).toContainText(TEACHER.username);
    await expect(page.locator('#createPollForm')).toBeVisible();
  });
  
  test('Login as student', async ({ page }) => {
    // Fill login form
    await page.locator('#username').fill(STUDENT.username);
    await page.locator('#password').fill(STUDENT.password);
    await page.locator('#isTeacher').not.toBeChecked();
    await page.locator('button:has-text("Login")').click();
    
    // Verify successful login
    await expect(page.locator('#userDisplay')).toContainText(STUDENT.username);
    await expect(page.locator('#createPollForm')).not.toBeVisible();
  });
  
  test('Failed login with invalid credentials', async ({ page }) => {
    // Fill login form with invalid credentials
    await page.locator('#username').fill('invalid');
    await page.locator('#password').fill('wrong');
    await page.locator('button:has-text("Login")').click();
    
    // Verify error message
    await expect(page.locator('#alertContainer')).toContainText(/Error/);
  });
  
  test('Poll creation and viewing workflow', async ({ page }) => {
    // Login as teacher
    await page.locator('#username').fill(TEACHER.username);
    await page.locator('#password').fill(TEACHER.password);
    await page.locator('#isTeacher').check();
    await page.locator('button:has-text("Login")').click();
    
    // Wait for login to complete
    await expect(page.locator('#userDisplay')).toContainText(TEACHER.username);
    
    // Create a new poll
    await page.locator('#pollQuestion').fill(TEST_POLL.question);
    await page.locator('#courseId').fill(TEST_POLL.courseId);
    
    // Fill in options (first two inputs are pre-created)
    const optionInputs = page.locator('.option-input');
    await optionInputs.nth(0).fill(TEST_POLL.options[0]);
    await optionInputs.nth(1).fill(TEST_POLL.options[1]);
    
    // Add another option if needed
    if (TEST_POLL.options.length > 2) {
      await page.locator('button:has-text("+ Add Option")').click();
      await page.locator('.option-input').nth(2).fill(TEST_POLL.options[2]);
    }
    
    // Submit the form
    await page.locator('button:has-text("Create Poll")').click();
    
    // Verify success message
    await expect(page.locator('#alertContainer')).toContainText(/Success/);
    await expect(page.locator('#alertContainer')).toContainText(/Poll created successfully/);
    
    // Check if the poll is displayed in the polls list
    await expect(page.locator('.poll-list')).toContainText(TEST_POLL.question);
  });
  
  test('Student voting workflow', async ({ page }) => {
    // Login as student
    await page.locator('#username').fill(STUDENT.username);
    await page.locator('#password').fill(STUDENT.password);
    await page.locator('button:has-text("Login")').click();
    
    // Wait for login to complete
    await expect(page.locator('#userDisplay')).toContainText(STUDENT.username);
    
    // Wait for polls to load
    await page.waitForSelector('.poll-card');
    
    // Click on the first poll's voting option
    const firstPoll = page.locator('.poll-card').first();
    await firstPoll.locator('.vote-option').first().click();
    
    // Verify success message for vote
    await expect(page.locator('#alertContainer')).toContainText(/Success/);
    await expect(page.locator('#alertContainer')).toContainText(/Vote recorded successfully/);
    
    // Results should now be visible
    await expect(firstPoll.locator('.progress')).toBeVisible();
  });
  
  test('View poll results', async ({ page }) => {
    // Login as teacher
    await page.locator('#username').fill(TEACHER.username);
    await page.locator('#password').fill(TEACHER.password);
    await page.locator('#isTeacher').check();
    await page.locator('button:has-text("Login")').click();
    
    // Wait for login to complete
    await expect(page.locator('#userDisplay')).toContainText(TEACHER.username);
    
    // Wait for polls to load
    await page.waitForSelector('.poll-card');
    
    // Click on "Show Results" for the first poll
    const firstPoll = page.locator('.poll-card').first();
    await firstPoll.locator('button.show-results-btn').click();
    
    // Verify results section becomes visible
    await expect(firstPoll.locator('.results-container')).toBeVisible();
    await expect(firstPoll.locator('.progress')).toBeVisible();
    await expect(firstPoll.locator('.result-item')).toBeVisible();
  });
  
  test('Close poll functionality', async ({ page }) => {
    // Login as teacher
    await page.locator('#username').fill(TEACHER.username);
    await page.locator('#password').fill(TEACHER.password);
    await page.locator('#isTeacher').check();
    await page.locator('button:has-text("Login")').click();
    
    // Wait for login to complete
    await expect(page.locator('#userDisplay')).toContainText(TEACHER.username);
    
    // Wait for polls to load
    await page.waitForSelector('.poll-card');
    
    // Create a new poll to close
    await page.locator('#pollQuestion').fill('Poll To Close');
    await page.locator('#courseId').fill(TEST_POLL.courseId);
    await page.locator('.option-input').nth(0).fill('Option X');
    await page.locator('.option-input').nth(1).fill('Option Y');
    await page.locator('button:has-text("Create Poll")').click();
    
    // Wait for the new poll to appear
    await page.waitForSelector('text=Poll To Close');
    
    // Find and close this specific poll
    const pollToClose = page.locator('.poll-card:has-text("Poll To Close")');
    await pollToClose.locator('button.close-poll-btn').click();
    
    // Confirm in the dialog
    await page.locator('button:has-text("Yes, close poll")').click();
    
    // Verify success message
    await expect(page.locator('#alertContainer')).toContainText(/Success/);
    await expect(page.locator('#alertContainer')).toContainText(/Poll closed successfully/);
    
    // Verify poll is marked as closed
    await expect(pollToClose.locator('.badge')).toContainText(/Closed/);
  });
  
  test('Logout functionality', async ({ page }) => {
    // Login first
    await page.locator('#username').fill(STUDENT.username);
    await page.locator('#password').fill(STUDENT.password);
    await page.locator('button:has-text("Login")').click();
    
    // Verify successful login
    await expect(page.locator('#userDisplay')).toContainText(STUDENT.username);
    
    // Logout
    await page.locator('button:has-text("Logout")').click();
    
    // Verify login form is shown again
    await expect(page.locator('#loginForm')).toBeVisible();
    await expect(page.locator('#userInfo')).not.toBeVisible();
  });
});