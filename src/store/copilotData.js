export const suggestedPrompts = [
  'Seminar Hall is available.',
  'Arduino stock is running low.',
  '12 students match this bounty.',
  'Generate procurement request.',
  'Inventory will be insufficient.',
  'Suggest a workshop topic.',
  'Analyze event attendance.',
  'Compare club performance.',
];

export const demoMessages = [
  {
    id: 1,
    role: 'assistant',
    text: 'Hello! I\'m your DRIVEN Copilot. I can help you manage events, inventory, and more. Try one of the suggestions below or ask me anything.',
    timestamp: 'Just now',
  },
  {
    id: 2,
    role: 'assistant',
    text: 'Seminar Hall is available this Friday. Would you like to book it for an event?',
    timestamp: '2m ago',
    actions: [
      { label: 'Book Seminar Hall', variant: 'primary' },
      { label: 'Dismiss', variant: 'ghost' },
    ],
  },
  {
    id: 3,
    role: 'user',
    text: 'Check inventory status',
    timestamp: '5m ago',
  },
  {
    id: 4,
    role: 'assistant',
    text: 'Only 3 Arduino Uno boards remaining. I recommend creating a procurement request to restock.',
    timestamp: '5m ago',
    actions: [
      { label: 'Generate Procurement', variant: 'primary' },
      { label: 'View Inventory', variant: 'ghost' },
    ],
  },
  {
    id: 5,
    role: 'assistant',
    text: 'I found 3 similar resolved issues in the support desk that may help with your current ticket.',
    timestamp: '8m ago',
    actions: [
      { label: 'View Similar Issues', variant: 'primary' },
    ],
  },
];

export const aiRecommendations = {
  event: {
    title: 'AI Recommendation',
    icon: 'stars',
    message: 'Seminar Hall is available this Friday. Perfect for a last-minute workshop.',
    action: 'Switch Venue',
  },
  inventory: {
    title: 'AI Alert',
    icon: 'exclamation-triangle-fill',
    message: 'Only 3 Arduino Uno boards remaining. Current stock may not last the week.',
    action: 'Generate Procurement',
  },
  support: {
    title: 'AI Analysis',
    icon: 'search-heart-fill',
    message: 'Found 3 similar resolved issues that match this ticket description.',
    action: 'View Similar',
  },
  bounty: {
    title: 'AI Match',
    icon: 'people-fill',
    message: '12 students match the requirements for this bounty opportunity.',
    action: 'View Matches',
  },
};
