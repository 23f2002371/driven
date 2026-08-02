import { reactive } from 'vue';

const clubs = [
  { name: 'TechNova', logo: 'TN', color: '#818cf8' },
  { name: 'DevSquad', logo: 'DS', color: '#34d399' },
  { name: 'Neural Ninjas', logo: 'NN', color: '#f472b6' },
  { name: 'AeroClub', logo: 'AC', color: '#60a5fa' },
  { name: 'IoT Guild', logo: 'IG', color: '#fbbf24' },
  { name: 'Web3 Wizards', logo: 'WW', color: '#a78bfa' },
];

const difficultyLevels = ['Easy', 'Medium', 'Advanced'];

export const store = reactive({
  currentUserRole: 'home',
  viewingEventDetails: null,
  registeredEvents: [3, 5, 6],
  showRegistrationModal: false,
  studentProfile: {
    fullName: 'Rahul Sharma',
    studentId: 'CS2024001',
    email: 'rahul.sharma@university.edu',
    phone: '+91 98765 43210',
    department: 'Computer Science',
    yearSemester: '3rd Year / 6th Sem',
    github: 'rahulsharma-dev',
    linkedin: 'rahulsharma',
    portfolio: 'https://rahulsharma.dev',
    tshirtSize: 'M',
    dietaryPreference: 'Vegetarian',
    emergencyName: 'Mr. Rajesh Sharma',
    emergencyPhone: '+91 98765 43211',
  },

  events: [
    { id: 1, name: 'IoT Workshop', date: 'Jul 15, 2026', venue: 'Lab A', status: 'Approved', participants: 45, description: 'Hands-on IoT building with Arduino sensors and microcontrollers.', image: 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop', deadline: 'Jul 10, 2026' },
    { id: 2, name: 'Hackathon 2026', date: 'Jul 22, 2026', venue: 'Auditorium', status: 'Approved', participants: 120, description: 'Annual 24-hour coding contest with prizes worth ₹50k.', image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&h=400&fit=crop', deadline: 'Jul 18, 2026' },
    { id: 3, name: 'Python Bootcamp', date: 'Jul 28, 2026', venue: 'Lab B', status: 'Approved', participants: 30, description: 'Introductory Python session covering data structures and algorithms.', image: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600&h=400&fit=crop', deadline: 'Jul 20, 2026' },
    { id: 4, name: 'AI/ML Seminar', date: 'Jul 25, 2026', venue: 'Seminar Hall', status: 'Pending', participants: 60, description: 'Deep dive into neural networks and transformer architectures.', image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop', deadline: 'Jul 20, 2026' },
    { id: 5, name: 'Web3 Hack Night', date: 'Aug 5, 2026', venue: 'Innovation Lab', status: 'Approved', participants: 50, description: 'Build dApps on Ethereum and explore Solidity fundamentals.', image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=600&h=400&fit=crop', deadline: 'Aug 3, 2026' },
    { id: 6, name: 'Drone Workshop', date: 'Aug 12, 2026', venue: 'Robotics Lab', status: 'Approved', participants: 25, description: 'Build and fly your own drone from scratch.', image: 'https://images.unsplash.com/photo-1508614589041-895f88991d0c?w=600&h=400&fit=crop', deadline: 'Aug 10, 2026' },
  ],

  inventory: [
    { id: 1, name: 'Arduino Uno', category: 'Microcontroller', available: 12, borrowed: 3, image: 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=400&h=300&fit=crop', description: 'Versatile microcontroller board for prototyping and IoT projects. Perfect for robotics and sensor integration.', borrowers: [{ name: 'Rahul Sharma', email: 'rahul.sharma@university.edu', qty: 2 }, { name: 'Priya Singh', email: 'priya.singh@university.edu', qty: 1 }], returnDeadline: 'Aug 10, 2026' },
    { id: 2, name: 'Raspberry Pi 4', category: 'SBC', available: 5, borrowed: 5, image: 'https://images.unsplash.com/photo-1630267988726-3bc3fc6c619a?w=400&h=300&fit=crop', description: 'Powerful single-board computer ideal for AI, media servers, and embedded applications with 4GB RAM.', borrowers: [{ name: 'Arun Kumar', email: 'arun.kumar@university.edu', qty: 1 }, { name: 'Neha Patel', email: 'neha.patel@university.edu', qty: 2 }, { name: 'Vikram Reddy', email: 'vikram.reddy@university.edu', qty: 2 }], returnDeadline: 'Aug 15, 2026' },
    { id: 3, name: 'Projector', category: 'AV Equipment', available: 2, borrowed: 1, image: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=300&fit=crop', description: 'High-lumen LED projector with HDMI input, suitable for presentations, screenings, and workshop demos.', borrowers: [{ name: 'Sneha Gupta', email: 'sneha.gupta@university.edu', qty: 1 }], returnDeadline: 'Aug 8, 2026' },
    { id: 4, name: 'Sensors Kit', category: 'Components', available: 16, borrowed: 4, image: 'https://images.unsplash.com/photo-1581092335397-9583eb92d232?w=400&h=300&fit=crop', description: 'Comprehensive sensor bundle including temperature, humidity, ultrasonic, motion, and light sensors.', borrowers: [{ name: 'Amit Sharma', email: 'amit.sharma@university.edu', qty: 2 }, { name: 'Divya Jain', email: 'divya.jain@university.edu', qty: 2 }], returnDeadline: 'Aug 12, 2026' },
    { id: 5, name: 'Drone Kit', category: 'Robotics', available: 4, borrowed: 2, image: 'https://images.unsplash.com/photo-1508614589041-895f88991d0c?w=400&h=300&fit=crop', description: 'DIY quadcopter frame with motors, ESCs, flight controller, and camera mount for aerial projects.', borrowers: [{ name: 'Karan Mehta', email: 'karan.mehta@university.edu', qty: 1 }, { name: 'Ritu Verma', email: 'ritu.verma@university.edu', qty: 1 }], returnDeadline: 'Aug 18, 2026' },
    { id: 6, name: 'VR Headset', category: 'AV Equipment', available: 3, borrowed: 0, image: 'https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=400&h=300&fit=crop', description: 'Immersive virtual reality headset with motion controllers, ideal for VR development and interactive demos.', borrowers: [], returnDeadline: 'N/A' },
  ],

  tickets: [
    {
      id: 1, student: 'Rahul Sharma', avatar: 'RS', department: 'Computer Science', email: 'rahul.sharma@university.edu', contact: '+91 98765 43210',
      subject: 'Unable to register for Hackathon - getting error',
      description: 'I am trying to register for the Hackathon 2026 event but I keep getting a "Server Error" message when I click the Register button. I have tried on multiple devices and browsers including Chrome, Firefox, and Edge. The error appears right after I enter my details and click submit. I have cleared my cache and cookies but the issue persists.',
      category: 'Event Registration', priority: 'High', status: 'Open', relatedEvent: 'Hackathon 2026',
      createdAt: 'Jul 20, 2026 at 10:30 AM', lastUpdated: 'Jul 20, 2026 at 2:15 PM',
      attachments: ['error_screenshot.png'],
      messages: [
        { id: 1, from: 'student', text: 'I am trying to register for the Hackathon 2026 but I keep getting a "Server Error" message when I click the Register button. I have tried on Chrome, Firefox, and Edge - same issue on all browsers.', timestamp: 'Jul 20, 10:30 AM', attachments: ['error_screenshot.png'] },
        { id: 2, from: 'admin', text: 'Thank you for reporting this, Rahul. Our team is looking into the issue. Could you please try clearing your browser cache and cookies, then attempt again? Also, please let us know which browser version you are using.', timestamp: 'Jul 20, 11:45 AM' },
        { id: 3, from: 'student', text: 'I already cleared cache and cookies. I am using Chrome 126 and Firefox 128. The issue is still there.', timestamp: 'Jul 20, 1:00 PM' },
        { id: 4, from: 'admin', text: 'We have identified the issue - it was a server-side validation bug that affected registration for events with participant limits. The fix has been deployed. Could you please try registering again?', timestamp: 'Jul 20, 2:15 PM' }
      ]
    },
    {
      id: 2, student: 'Priya Kaur', avatar: 'PK', department: 'Electronics Engineering', email: 'priya.kaur@university.edu', contact: '+91 87654 32109',
      subject: 'Need Arduino returned by Friday for project',
      description: 'I borrowed an Arduino Uno from the lab last week for my IoT project. The standard borrowing period ends tomorrow, but I need a few more days to complete my circuit testing. Could you please extend the deadline until Monday? I will make sure to return it in good condition.',
      category: 'Equipment Request', priority: 'Medium', status: 'Resolved', relatedEquipment: 'Arduino Uno',
      createdAt: 'Jul 18, 2026 at 9:15 AM', lastUpdated: 'Jul 18, 2026 at 3:30 PM',
      attachments: [],
      messages: [
        { id: 1, from: 'student', text: 'I borrowed an Arduino Uno last week for my IoT project. The standard borrowing period ends tomorrow but I need a few more days to complete my circuit testing. Could you please extend the deadline until Monday?', timestamp: 'Jul 18, 9:15 AM' },
        { id: 2, from: 'admin', text: 'We have extended your deadline to Monday. Please ensure the equipment is returned in good condition by Monday evening. Let us know if you need any further assistance.', timestamp: 'Jul 18, 3:30 PM' }
      ]
    },
    {
      id: 3, student: 'Ankit Verma', avatar: 'AV', department: 'Mechanical Engineering', email: 'ankit.verma@university.edu', contact: '+91 76543 21098',
      subject: 'Projector bulb not working in Lab B',
      description: 'The projector in Lab B (Room 204) has a blown bulb. When I turn it on, the power light comes on but after about 30 seconds it shuts down with a blinking red light. This is the second time this month this has happened. We need this for our workshop presentation tomorrow.',
      category: 'Facility Issue', priority: 'Low', status: 'Open', relatedEquipment: 'Projector',
      createdAt: 'Jul 21, 2026 at 4:00 PM', lastUpdated: 'Jul 21, 2026 at 4:00 PM',
      attachments: [],
      messages: [
        { id: 1, from: 'student', text: 'The projector in Lab B (Room 204) has a blown bulb. When I turn it on, the power light comes on but after about 30 seconds it shuts down with a blinking red light. This is the second time this month. We need this for our workshop presentation tomorrow.', timestamp: 'Jul 21, 4:00 PM' }
      ]
    },
    {
      id: 4, student: 'Neha Patel', avatar: 'NP', department: 'AI & ML', email: 'neha.patel@university.edu', contact: '+91 65432 10987',
      subject: 'Requesting access to VR Headset for research',
      description: 'I am working on a research project about immersive learning environments and need access to the VR Headset for testing. I would like to borrow it for a week. I have prior experience with VR development and can handle the equipment responsibly.',
      category: 'Equipment Request', priority: 'Low', status: 'Open', relatedEquipment: 'VR Headset',
      createdAt: 'Jul 21, 2026 at 11:00 AM', lastUpdated: 'Jul 21, 2026 at 11:00 AM',
      attachments: ['research_proposal.pdf'],
      messages: [
        { id: 1, from: 'student', text: 'I am working on a research project about immersive learning environments and need access to the VR Headset for testing. I would like to borrow it for a week starting next Monday. I have attached my research proposal for your reference.', timestamp: 'Jul 21, 11:00 AM', attachments: ['research_proposal.pdf'] }
      ]
    },
  ],

  bookedDates: [5, 10, 12, 15, 18, 22, 26],

  projects: [
    { id: 1, title: 'Smart Agri Monitor', team: 'Team AgriTech', event: 'IoT Workshop', description: 'Automated soil monitoring & irrigation system using Arduino sensors.', image: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=600&h=400&fit=crop' },
    { id: 2, title: 'Campus Connect', team: 'DevSquad', event: 'Hackathon 2026', description: 'Real-time campus collaboration & event discovery platform.', image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop' },
    { id: 3, title: 'CodeLens AI', team: 'Neural Ninjas', event: 'AI/ML Seminar', description: 'AI-powered code review assistant built with Python & TensorFlow.', image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop' },
    { id: 4, title: 'Drone Swarm', team: 'AeroClub', event: 'IoT Workshop', description: 'Autonomous drone coordination system for surveillance & delivery.', image: 'https://images.unsplash.com/photo-1508614589041-895f88991d0c?w=600&h=400&fit=crop' },
    { id: 5, title: 'NFT Gallery', team: 'Web3 Wizards', event: 'Web3 Hack Night', description: 'Decentralized NFT minting platform for student artwork.', image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=600&h=400&fit=crop' },
    { id: 6, title: 'EcoBot', team: 'Green Coders', event: 'Drone Workshop', description: 'Solar-powered autonomous garbage collection drone.', image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&h=400&fit=crop' },
  ],

  reviews: [
    { id: 1, name: 'Priya Sharma', role: 'CS Sophomore', text: 'DRIVEN made organizing our college hackathon seamless. The inventory tracking and venue booking saved us hours of manual work!', rating: 5, avatar: 'PS' },
    { id: 2, name: 'Arjun Mehta', role: 'Club Lead, TechNova', text: 'As a club admin, I love how everything syncs — events, approvals, equipment. It\'s the backbone of our club operations now.', rating: 5, avatar: 'AM' },
    { id: 3, name: 'Neha Patel', role: 'Lab Assistant', text: 'Equipment borrowing used to be chaos. Now students borrow and return with one click, and I can track everything in real time.', rating: 4, avatar: 'NP' },
    { id: 4, name: 'Rahul Verma', role: 'Student Developer', text: 'From registering for events to checking equipment availability, DRIVEN is my go-to for everything club-related. Amazing platform!', rating: 5, avatar: 'RV' },
    { id: 5, name: 'Sneha Reddy', role: 'Club Admin, AeroClub', text: 'The QR-based attendance tracking alone saved us hours. DRIVEN is a must-have for any serious tech club on campus.', rating: 5, avatar: 'SR' },
  ],

  eventWinners: [
    {
      id: 1, eventName: 'Drone Workshop', eventDate: 'Aug 12, 2026',
      first: { team: 'SkyForge', members: 4, project: 'Autonomous Delivery Drone', initials: 'SF', color: '#f59e0b' },
      second: { team: 'AeroPulse', members: 3, project: 'Search & Rescue Drone', initials: 'AP', color: '#94a3b8' },
      third: { team: 'DroneX', members: 3, project: 'Drone Light Show', initials: 'DX', color: '#d97706' },
    },
    {
      id: 2, eventName: 'Web3 Hack Night', eventDate: 'Aug 5, 2026',
      first: { team: 'ChainForge', members: 4, project: 'NFT Gallery', initials: 'CF', color: '#f59e0b' },
      second: { team: 'BlockStars', members: 3, project: 'DeFi Dashboard', initials: 'BS', color: '#94a3b8' },
      third: { team: 'MetaCraft', members: 4, project: 'Web3 Wallet', initials: 'MC', color: '#d97706' },
    },
    {
      id: 3, eventName: 'Hackathon 2026', eventDate: 'Jul 22, 2026',
      first: { team: 'DevSquad', members: 5, project: 'Campus Connect', initials: 'DS', color: '#f59e0b' },
      second: { team: 'Neural Ninjas', members: 4, project: 'CodeLens AI', initials: 'NN', color: '#94a3b8' },
      third: { team: 'AgriTech', members: 3, project: 'Smart Agri Monitor', initials: 'AT', color: '#d97706' },
    },
    {
      id: 4, eventName: 'IoT Workshop', eventDate: 'Jul 15, 2026',
      first: { team: 'RoboWarriors', members: 4, project: 'IoT Smart Farm', initials: 'RW', color: '#f59e0b' },
      second: { team: 'SensorSquad', members: 3, project: 'Weather Station', initials: 'SS', color: '#94a3b8' },
      third: { team: 'CircuitBreakers', members: 3, project: 'Home Automation', initials: 'CB', color: '#d97706' },
    },
  ],

  gallery: [
    { id: 1, image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&h=600&fit=crop', caption: 'Hackathon 2026 Grand Finale' },
    { id: 2, image: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=800&h=600&fit=crop', caption: 'IoT Workshop - Hands on Session' },
    { id: 3, image: 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800&h=600&fit=crop', caption: 'AI/ML Seminar - Guest Lecture' },
    { id: 4, image: 'https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=800&h=600&fit=crop', caption: 'Tech Talk - Industry Experts' },
    { id: 5, image: 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&h=600&fit=crop', caption: 'Web3 Hack Night - Coding Sprint' },
    { id: 6, image: 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&h=600&fit=crop', caption: 'Drone Workshop - Flight Test' },
  ],

  labSlots: [
    { id: 'A', name: 'IoT Lab', status: 'booked', event: 'IoT Workshop', time: '2:00 PM - 5:00 PM', capacity: 30 },
    { id: 'B', name: 'AI Lab', status: 'available', event: '', time: '', capacity: 25 },
    { id: 'C', name: 'Robotics Lab', status: 'booked', event: 'Drone Assembly', time: '3:00 PM - 6:00 PM', capacity: 20 },
    { id: 'D', name: 'Seminar Hall', status: 'available', event: '', time: '', capacity: 60 },
    { id: 'E', name: 'Auditorium', status: 'booked', event: 'Tech Talk Prep', time: '4:00 PM - 7:00 PM', capacity: 120 },
    { id: 'F', name: 'Innovation Lab', status: 'available', event: '', time: '', capacity: 40 },
  ],

  notifications: [],

  certificates: [
    { id: 1, eventName: 'IoT Workshop', type: 'Participation', issueDate: 'Jul 16, 2026', organizer: 'TechNova Club', image: 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop' },
    { id: 2, eventName: 'Hackathon 2026', type: 'Winner', issueDate: 'Jul 23, 2026', organizer: 'TechNova Club', image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&h=400&fit=crop' },
    { id: 3, eventName: 'AI/ML Seminar', type: 'Participation', issueDate: 'Jul 26, 2026', organizer: 'TechNova Club', image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop' },
  ],

  bounties: [
    {
      id: 1, title: 'Build Hackathon Website',
      clubName: 'TechNova', clubLogo: 'TN', clubColor: '#818cf8',
      description: 'Design and develop a responsive landing page for Hackathon 2026 with registration forms, schedule, and sponsor sections.',
      fullDescription: 'We need a talented frontend developer to create an engaging, responsive landing page for our annual Hackathon 2026. The page should include a hero section, event schedule, sponsor showcase, FAQ accordion, and registration form integration. The design should follow our brand guidelines with a modern, tech-forward aesthetic.',
      responsibilities: ['Design responsive landing page', 'Implement registration form with validation', 'Create schedule/timeline section', 'Add sponsor carousel', 'Ensure cross-browser compatibility'],
      category: 'Web Development',
      skills: ['React', 'CSS', 'JavaScript', 'Responsive Design'],
      reward: '₹2,500', deadline: 'Aug 15, 2026', duration: '2 Weeks',
      deliverables: ['Complete landing page code', 'Design assets (Figma files)', 'Documentation'],
      difficulty: 'Intermediate', applicantsCount: 4, timePosted: '2 days ago',
      clubEmail: 'technova@university.edu', status: 'open',
      image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop',
    },
    {
      id: 2, title: 'Mobile App UI Design',
      clubName: 'DevSquad', clubLogo: 'DS', clubColor: '#34d399',
      description: 'Create a modern mobile UI design for a campus social networking app with dark mode support and micro-interactions.',
      fullDescription: 'DevSquad is looking for a UI/UX designer to create a comprehensive mobile app design for "Campus Connect" - a social networking platform for students. The design should include onboarding screens, feed, messaging, profile, and notification screens with smooth micro-interactions.',
      responsibilities: ['Design mobile UI screens', 'Create interactive prototype', 'Design system documentation', 'Dark mode variant', 'Handoff to developers'],
      category: 'UI/UX Design',
      skills: ['Figma', 'UI Design', 'Prototyping', 'Design Systems'],
      reward: '₹3,000', deadline: 'Aug 20, 2026', duration: '3 Weeks',
      deliverables: ['Figma file with all screens', 'Interactive prototype', 'Design system guide'],
      difficulty: 'Medium', applicantsCount: 7, timePosted: '5 days ago',
      clubEmail: 'devsquad@university.edu', status: 'open',
      image: 'https://images.unsplash.com/photo-1551650975-87deedd944c3?w=600&h=400&fit=crop',
    },
    {
      id: 3, title: 'ML Data Pipeline',
      clubName: 'Neural Ninjas', clubLogo: 'NN', clubColor: '#f472b6',
      description: 'Build a data preprocessing and feature engineering pipeline for a machine learning model that predicts student performance.',
      fullDescription: 'Neural Ninjas needs a data engineer to build an automated data preprocessing pipeline. The project involves cleaning, transforming, and feature engineering on a dataset of 50,000 student records to train predictive models for academic performance.',
      responsibilities: ['Data cleaning & preprocessing', 'Feature engineering', 'Pipeline automation', 'Documentation', 'Model evaluation support'],
      category: 'Data Science',
      skills: ['Python', 'Pandas', 'Scikit-learn', 'Jupyter'],
      reward: '₹4,000', deadline: 'Sep 1, 2026', duration: '4 Weeks',
      deliverables: ['Cleaned dataset', 'Feature engineering code', 'Pipeline scripts', 'Documentation'],
      difficulty: 'Advanced', applicantsCount: 2, timePosted: '1 week ago',
      clubEmail: 'neuralninjas@university.edu', status: 'open',
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop',
    },
    {
      id: 4, title: 'Drone Control Dashboard',
      clubName: 'AeroClub', clubLogo: 'AC', clubColor: '#60a5fa',
      description: 'Develop a real-time drone telemetry dashboard with GPS tracking, battery monitoring, and flight path visualization.',
      fullDescription: 'AeroClub requires a full-stack developer to build a real-time dashboard for monitoring drone fleets. The dashboard should display telemetry data including GPS coordinates, altitude, battery status, and flight paths on an interactive map.',
      responsibilities: ['Real-time data visualization', 'Interactive map integration', 'Telemetry dashboard UI', 'API integration', 'Alert system'],
      category: 'Full Stack',
      skills: ['React', 'Node.js', 'WebSockets', 'Mapbox'],
      reward: '₹5,000', deadline: 'Sep 10, 2026', duration: '5 Weeks',
      deliverables: ['Dashboard application', 'API endpoints', 'Real-time data feed', 'User documentation'],
      difficulty: 'Advanced', applicantsCount: 3, timePosted: '3 days ago',
      clubEmail: 'aeroclub@university.edu', status: 'open',
      image: 'https://images.unsplash.com/photo-1508614589041-895f88991d0c?w=600&h=400&fit=crop',
    },
    {
      id: 5, title: 'IoT Sensor Dashboard',
      clubName: 'IoT Guild', clubLogo: 'IG', clubColor: '#fbbf24',
      description: 'Create an IoT sensor data visualization dashboard with real-time charts, alerts, and device management.',
      fullDescription: 'IoT Guild needs a developer to build a monitoring dashboard for their network of environmental sensors deployed across campus. The dashboard should display temperature, humidity, air quality data with real-time updates and alerting.',
      responsibilities: ['Real-time chart visualizations', 'Device management UI', 'Alert configuration', 'Data export functionality', 'Responsive design'],
      category: 'Web Development',
      skills: ['Vue.js', 'D3.js', 'Node.js', 'MongoDB'],
      reward: '₹3,500', deadline: 'Aug 25, 2026', duration: '3 Weeks',
      deliverables: ['Dashboard code', 'API documentation', 'Deployment guide'],
      difficulty: 'Medium', applicantsCount: 5, timePosted: '1 day ago',
      clubEmail: 'iotguild@university.edu', status: 'open',
      image: 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop',
    },
    {
      id: 6, title: 'NFT Minting Platform',
      clubName: 'Web3 Wizards', clubLogo: 'WW', clubColor: '#a78bfa',
      description: 'Build a simple NFT minting dApp with a React frontend and Solidity smart contracts for student artwork.',
      fullDescription: 'Web3 Wizards is looking for a blockchain developer to build a prototype NFT minting platform where students can mint their artwork as NFTs. The project includes a React frontend, Solidity smart contracts, and IPFS integration for metadata storage.',
      responsibilities: ['Smart contract development', 'React frontend', 'Wallet integration', 'IPFS metadata storage', 'Testing & deployment'],
      category: 'Blockchain',
      skills: ['Solidity', 'React', 'Ethers.js', 'Hardhat'],
      reward: '₹6,000', deadline: 'Sep 5, 2026', duration: '4 Weeks',
      deliverables: ['Smart contracts', 'Frontend dApp', 'Deployment scripts', 'Technical documentation'],
      difficulty: 'Advanced', applicantsCount: 1, timePosted: '1 week ago',
      clubEmail: 'web3wizards@university.edu', status: 'open',
      image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=600&h=400&fit=crop',
    },
  ],

  studentSkills: [
    { name: 'React', level: 4 },
    { name: 'Node.js', level: 5 },
    { name: 'Python', level: 4 },
    { name: 'UI/UX', level: 3 },
    { name: 'Docker', level: 4 },
    { name: 'MongoDB', level: 3 },
    { name: 'JavaScript', level: 5 },
    { name: 'TypeScript', level: 4 },
    { name: 'Figma', level: 3 },
    { name: 'CSS', level: 4 },
  ],

  portfolio: [
    { id: 1, title: 'Frontend Developer', project: 'Hackathon Website', clubName: 'TechNova', verified: true, duration: 'Jul 2026', description: 'Built the complete frontend for the annual hackathon website including responsive design, registration forms, schedule sections, and sponsor carousel using React and CSS.', skills: ['React', 'CSS', 'JavaScript'], badge: 'Top Performer', certificateUrl: '#' },
    { id: 2, title: 'UI/UX Designer', project: 'Campus Connect App', clubName: 'DevSquad', verified: true, duration: 'Jun 2026', description: 'Designed a complete mobile UI for the campus social networking app including onboarding, feed, messaging, and profile screens with dark mode support.', skills: ['Figma', 'UI Design', 'Prototyping'], badge: 'Design Excellence', certificateUrl: '#' },
    { id: 3, title: 'Data Analyst', project: 'Student Performance ML', clubName: 'Neural Ninjas', verified: true, duration: 'May 2026', description: 'Built an automated data preprocessing pipeline for student performance prediction including data cleaning, feature engineering, and model evaluation.', skills: ['Python', 'Pandas', 'Scikit-learn'], badge: 'Verified', certificateUrl: '#' },
  ],

  myApplications: [
    { id: 1, bountyId: 1, status: 'accepted', submittedAt: 'Jul 21, 2026', why: 'I have extensive experience building React applications and have won 2 hackathons. This project aligns perfectly with my skills.', experience: 'Built 3 React projects including a real-time chat app and an e-commerce dashboard. Contributed to open-source React component library.', github: 'https://github.com/rahulsharma', portfolio: 'https://rahulsharma.dev', resume: null, availability: '20 hrs/week', deliverables: null, submission: null },
    { id: 2, bountyId: 2, status: 'pending', submittedAt: 'Jul 22, 2026', why: 'I am passionate about UI/UX design and have been using Figma for 2 years. I would love to contribute to the campus social app.', experience: 'Designed 5+ mobile app interfaces. Created a design system for a college project management tool.', github: 'https://github.com/rahulsharma', portfolio: 'https://dribbble.com/rahulsharma', resume: null, availability: '15 hrs/week', deliverables: null, submission: null },
  ],

  adminBounties: [],
  bountyApplicants: {},

  categoryFilters: ['All', 'Web Development', 'UI/UX Design', 'Data Science', 'Full Stack', 'Blockchain', 'Mobile'],
  skillFilters: ['All', 'React', 'Vue.js', 'Python', 'Node.js', 'Figma', 'Solidity', 'CSS', 'JavaScript', 'TypeScript'],

  volunteerSkills: [
    'Photography', 'Video Editing', 'Graphic Design', 'Public Speaking',
    'Event Management', 'Social Media', 'Registration Desk', 'Technical Support',
    'Logistics', 'Content Writing',
  ],

  volunteerApplications: [
    {
      id: 1, eventId: 2, status: 'accepted',
      eventName: 'Hackathon 2026', clubName: 'TechNova',
      date: 'Jul 22, 2026', venue: 'Auditorium',
      image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&h=400&fit=crop',
      role: 'Registration Desk',
      assignedTask: 'Manage Registration Desk',
      taskDescription: 'Handle participant check-in, distribute event kits, and guide attendees to their designated sections. Coordinate with the technical team for any registration issues.',
      assignedBy: 'Arjun Mehta',
      reportingTime: '08:00 AM',
      volunteerLead: 'Priya Sharma',
      priority: 'high',
      completionDate: null,
      thankYouMessage: null,
      feedback: null,
      checklist: [
        { id: 1, label: 'Set up registration desk', completed: true },
        { id: 2, label: 'Arrange event kits and badges', completed: true },
        { id: 3, label: 'Coordinate with tech team', completed: false },
        { id: 4, label: 'Manage check-in queue', completed: false },
        { id: 5, label: 'Submit attendance report', completed: false },
      ],
      dressCode: 'Club T-shirt + ID Card',
      notes: 'Report to the main lobby entrance. Breakfast will be provided.',
    },
    {
      id: 2, eventId: 1, status: 'pending',
      eventName: 'IoT Workshop', clubName: 'TechNova',
      date: 'Jul 15, 2026', venue: 'Lab A',
      image: 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop',
      role: 'Technical Support',
      assignedTask: null,
      taskDescription: null,
      assignedBy: null,
      reportingTime: null,
      volunteerLead: null,
      priority: null,
      completionDate: null,
      thankYouMessage: null,
      feedback: null,
      checklist: [],
      dressCode: null,
      notes: null,
    },
    {
      id: 3, eventId: 4, status: 'rejected',
      eventName: 'AI/ML Seminar', clubName: 'TechNova',
      date: 'Jul 25, 2026', venue: 'Seminar Hall',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop',
      role: 'Photography',
      assignedTask: null,
      taskDescription: null,
      assignedBy: null,
      reportingTime: null,
      volunteerLead: null,
      priority: null,
      completionDate: null,
      thankYouMessage: null,
      feedback: 'We received many applications for Photography. Unfortunately, we had limited slots. Please try again for our next event.',
      checklist: [],
      dressCode: null,
      notes: null,
    },
    {
      id: 4, eventId: 5, status: 'completed',
      eventName: 'Web3 Hack Night', clubName: 'Web3 Wizards',
      date: 'Aug 5, 2026', venue: 'Innovation Lab',
      image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=600&h=400&fit=crop',
      role: 'Stage Management',
      assignedTask: 'Coordinate Speakers',
      taskDescription: 'Managed speaker schedule, stage setup, and presentation transitions throughout the event.',
      assignedBy: 'Rahul Verma',
      reportingTime: '04:00 PM',
      volunteerLead: 'Neha Patel',
      priority: 'medium',
      completionDate: 'Aug 5, 2026',
      thankYouMessage: 'Thank you for your excellent coordination! The event ran smoothly because of your efforts.',
      feedback: null,
      checklist: [
        { id: 1, label: 'Coordinate speaker arrival', completed: true },
        { id: 2, label: 'Setup stage and AV equipment', completed: true },
        { id: 3, label: 'Manage presentation transitions', completed: true },
        { id: 4, label: 'Collect feedback forms', completed: true },
      ],
      dressCode: 'Formal attire',
      notes: 'Great job managing the stage!',
    },
  ],

  registrationDrafts: [],

  saveRegistrationDraft(draft) {
    const idx = this.registrationDrafts.findIndex(d => d.eventId === draft.eventId);
    if (idx >= 0) {
      this.registrationDrafts[idx] = { ...this.registrationDrafts[idx], ...draft, updatedAt: new Date().toISOString() };
    } else {
      this.registrationDrafts.push({ ...draft, id: Date.now(), createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() });
    }
  },

  getRegistrationDraft(eventId) {
    return this.registrationDrafts.find(d => d.eventId === eventId) || null;
  },

  generateRegistrationId() {
    return 'DRVN-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).substring(2, 6).toUpperCase();
  },

  addNotification(notification) {
    this.notifications.unshift({
      id: Date.now() + Math.random(),
      timestamp: new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }),
      read: false,
      ...notification,
    });
  },

  markNotifRead(id) {
    const n = this.notifications.find(n => n.id === id);
    if (n) n.read = true;
  },

  clearNotifsForRole(role) {
    this.notifications = this.notifications.filter(n => n.role !== role);
  },

  addEvent(newEvent) {
    const event = { id: Date.now(), deadline: newEvent.date || '', ...newEvent, status: 'Pending', image: 'https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop' };
    this.events.push(event);
    this.addNotification({ type: 'event_created', message: `New event "${newEvent.name}" created and pending approval`, role: 'lab_admin', icon: 'calendar-plus', color: '#818cf8' });
  },
  approveEvent(id) {
    const event = this.events.find(e => e.id === id);
    if (event) {
      event.status = 'Approved';
      this.addNotification({ type: 'event_approved', message: `"${event.name}" has been approved by Lab Admin`, role: 'club_admin', icon: 'check-circle-fill', color: '#34d399' });
    }
  },
  rejectEvent(id) {
    const event = this.events.find(e => e.id === id);
    if (event) {
      event.status = 'Rejected';
      this.addNotification({ type: 'event_rejected', message: `"${event.name}" has been rejected by Lab Admin`, role: 'club_admin', icon: 'x-circle-fill', color: '#fb7185' });
    }
  },
  addTicket(newTicket) {
    const attachments = newTicket.attachments || [];
    this.tickets.unshift({
      id: Date.now(),
      student: 'Current Student',
      avatar: 'CS',
      department: 'Computer Science',
      email: 'student@university.edu',
      contact: '+91 90000 00000',
      status: 'Open',
      createdAt: new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }),
      lastUpdated: new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }),
      messages: [{ id: Date.now(), from: 'student', text: newTicket.description || '', timestamp: 'Just now', attachments }],
      attachments,
      ...newTicket
    });
    this.addNotification({ type: 'ticket_raised', message: `New support ticket: "${newTicket.subject}"`, role: 'club_admin', icon: 'ticket-perforated-fill', color: '#fbbf24' });
    this.addNotification({ type: 'ticket_confirmed', message: `Ticket "${newTicket.subject}" submitted successfully`, role: 'student', icon: 'check-circle-fill', color: '#34d399' });
  },
  studentReply(id, text) {
    const ticket = this.tickets.find(t => t.id === id);
    if (ticket) {
      ticket.messages.push({ id: Date.now(), from: 'student', text, timestamp: 'Just now' });
      ticket.lastUpdated = new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
    }
  },
  reopenTicket(id) {
    const ticket = this.tickets.find(t => t.id === id);
    if (ticket) {
      ticket.status = 'Open';
      ticket.lastUpdated = new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
    }
  },
  resolveTicket(id, replyText) {
    const ticket = this.tickets.find(t => t.id === id);
    if (ticket) {
      ticket.status = 'Resolved';
      if (replyText) {
        ticket.messages.push({ id: Date.now(), from: 'admin', text: replyText, timestamp: new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) });
      }
      ticket.lastUpdated = new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
      this.addNotification({ type: 'ticket_resolved', message: `Your ticket "${ticket.subject}" has been resolved`, role: 'student', icon: 'check-circle-fill', color: '#34d399' });
    }
  },
  borrowItem(id, quantity = 1) {
    const item = this.inventory.find(i => i.id === id);
    if (item && item.available >= quantity) {
      item.available -= quantity;
      item.borrowed += quantity;
      this.addNotification({ type: 'item_borrowed', message: `"${item.name}" ×${quantity} borrowed by a student`, role: 'club_admin', icon: 'box-seam-fill', color: '#60a5fa' });
      return true;
    }
    return false;
  },
  increaseItemQuantity(id, quantity = 1) {
    const item = this.inventory.find(i => i.id === id);
    if (item) {
      item.available += quantity;
      item.borrowed = Math.max(0, item.borrowed);
      this.addNotification({ type: 'stock_added', message: `"${item.name}" stock increased to ${item.available}`, role: 'club_admin', icon: 'plus-circle-fill', color: '#34d399' });
      return true;
    }
    return false;
  },
  returnItem(id, quantity = 1) {
    const item = this.inventory.find(i => i.id === id);
    if (item && item.borrowed >= quantity) {
      item.borrowed -= quantity;
      item.available += quantity;
      this.addNotification({ type: 'item_returned', message: `"${item.name}" ×${quantity} returned`, role: 'club_admin', icon: 'arrow-return-left', color: '#34d399' });
      return true;
    }
    return false;
  },

  submitVolunteerApplication(data) {
    const app = {
      id: Date.now(),
      eventId: data.eventId,
      status: 'pending',
      eventName: data.eventName,
      clubName: data.clubName,
      date: data.date,
      venue: data.venue,
      image: data.image,
      role: data.role || '',
      assignedTask: null,
      taskDescription: null,
      assignedBy: null,
      reportingTime: null,
      volunteerLead: null,
      priority: null,
      completionDate: null,
      thankYouMessage: null,
      feedback: null,
      checklist: [],
      dressCode: null,
      notes: null,
    };
    this.volunteerApplications.unshift(app);
    this.addNotification({ type: 'volunteer_applied', message: `Volunteer application submitted for "${data.eventName}"`, role: 'student', icon: 'hand-thumbs-up-fill', color: '#818cf8' });
  },

  markVolunteerTaskComplete(appId) {
    const app = this.volunteerApplications.find(a => a.id === appId);
    if (app) {
      app.status = 'completed';
      app.completionDate = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      app.thankYouMessage = 'Thank you for your contribution! Your efforts made the event a success.';
      app.checklist.forEach(item => { item.completed = true; });
    }
  }
});
