import type { Transaction, Card, Device, Identity } from "../types";

export const mockTransactions: Transaction[] = [
  { transactionId: "TXN-847291", customerId: "CUS-10482", customerName: "Priya Sharma",   amount: 1249.00, currency: "USD", channel: "E-commerce", timestamp: "2024-06-11T09:12:00Z", riskScore: 0.94, riskLevel: "very_high", status: "flagged",  cardId: "CARD-8831", deviceId: "DEV-91A2", merchant: "ShopEasy Global",  location: "Lagos, NG" },
  { transactionId: "TXN-847292", customerId: "CUS-10482", customerName: "Priya Sharma",   amount: 89.50,   currency: "USD", channel: "POS",        timestamp: "2024-06-11T08:55:00Z", riskScore: 0.42, riskLevel: "moderate",  status: "approved", cardId: "CARD-8831", deviceId: "DEV-91A2", merchant: "Cafe Mocha",       location: "Mumbai, IN" },
  { transactionId: "TXN-923812", customerId: "CUS-20391", customerName: "Rahul Mehta",    amount: 3200.00, currency: "USD", channel: "Wire",       timestamp: "2024-06-11T07:40:00Z", riskScore: 0.78, riskLevel: "high",      status: "pending",  cardId: "CARD-7712", deviceId: "DEV-72F1", merchant: "Global Remit",     location: "Dubai, AE" },
  { transactionId: "TXN-923813", customerId: "CUS-34821", customerName: "Ananya Iyer",    amount: 210.75,  currency: "USD", channel: "E-commerce", timestamp: "2024-06-10T21:30:00Z", riskScore: 0.62, riskLevel: "moderate",  status: "approved", cardId: "CARD-6611", deviceId: "DEV-3C91", merchant: "FashionHub",       location: "Bengaluru, IN" },
  { transactionId: "TXN-931044", customerId: "CUS-41120", customerName: "Vikram Nair",    amount: 45.00,   currency: "USD", channel: "UPI",        timestamp: "2024-06-10T18:12:00Z", riskScore: 0.23, riskLevel: "low",       status: "approved", cardId: "CARD-5520", deviceId: "DEV-1A44", merchant: "GroceryMart",      location: "Chennai, IN" },
  { transactionId: "TXN-931045", customerId: "CUS-50911", customerName: "Meera Krishnan", amount: 890.00,  currency: "USD", channel: "E-commerce", timestamp: "2024-06-11T07:20:00Z", riskScore: 0.91, riskLevel: "very_high", status: "flagged",  cardId: "CARD-4491", deviceId: "DEV-88B2", merchant: "TechWorld",        location: "Kyiv, UA" },
  { transactionId: "TXN-931046", customerId: "CUS-60233", customerName: "Arjun Verma",    amount: 340.00,  currency: "USD", channel: "POS",        timestamp: "2024-06-09T14:00:00Z", riskScore: 0.41, riskLevel: "moderate",  status: "approved", cardId: "CARD-3320", deviceId: "DEV-4D21", merchant: "ElectroCity",      location: "Pune, IN" },
  { transactionId: "TXN-931047", customerId: "CUS-70014", customerName: "Sneha Patel",    amount: 4500.00, currency: "USD", channel: "Wire",       timestamp: "2024-06-11T09:55:00Z", riskScore: 0.97, riskLevel: "very_high", status: "flagged",  cardId: "CARD-2210", deviceId: "DEV-91A2", merchant: "Overseas Transfer",location: "Unknown" },
  { transactionId: "TXN-931048", customerId: "CUS-81200", customerName: "Karthik Rao",    amount: 120.00,  currency: "USD", channel: "UPI",        timestamp: "2024-06-08T11:30:00Z", riskScore: 0.31, riskLevel: "low",       status: "approved", cardId: "CARD-1180", deviceId: "DEV-2F10", merchant: "BookNest",         location: "Hyderabad, IN" },
  { transactionId: "TXN-931049", customerId: "CUS-92017", customerName: "Divya Menon",    amount: 600.00,  currency: "USD", channel: "E-commerce", timestamp: "2024-06-10T15:50:00Z", riskScore: 0.55, riskLevel: "moderate",  status: "approved", cardId: "CARD-7702", deviceId: "DEV-6B33", merchant: "HomeStyle",        location: "Kochi, IN" },
  { transactionId: "TXN-931050", customerId: "CUS-98765", customerName: "Rohit Bansal",   amount: 1800.00, currency: "USD", channel: "Wire",       timestamp: "2024-06-11T06:30:00Z", riskScore: 0.81, riskLevel: "high",      status: "flagged",  cardId: "CARD-5540", deviceId: "DEV-72F1", merchant: "Overseas Transfer",location: "Unknown" },
  { transactionId: "TXN-931051", customerId: "CUS-10482", customerName: "Priya Sharma",   amount: 75.00,   currency: "USD", channel: "POS",        timestamp: "2024-06-10T20:11:00Z", riskScore: 0.28, riskLevel: "low",       status: "approved", cardId: "CARD-8831", deviceId: "DEV-91A2", merchant: "Pharmacy Plus",    location: "Mumbai, IN" },
  { transactionId: "TXN-931052", customerId: "CUS-20391", customerName: "Rahul Mehta",    amount: 410.00,  currency: "USD", channel: "E-commerce", timestamp: "2024-06-10T13:22:00Z", riskScore: 0.72, riskLevel: "high",      status: "approved", cardId: "CARD-7712", deviceId: "DEV-72F1", merchant: "GadgetZone",       location: "Delhi, IN" },
  { transactionId: "TXN-931053", customerId: "CUS-34821", customerName: "Ananya Iyer",    amount: 55.00,   currency: "USD", channel: "UPI",        timestamp: "2024-06-09T19:04:00Z", riskScore: 0.22, riskLevel: "low",       status: "approved", cardId: "CARD-6611", deviceId: "DEV-3C91", merchant: "FoodExpress",      location: "Bengaluru, IN" },
  { transactionId: "TXN-931054", customerId: "CUS-50911", customerName: "Meera Krishnan", amount: 2200.00, currency: "USD", channel: "Wire",       timestamp: "2024-06-10T22:45:00Z", riskScore: 0.88, riskLevel: "very_high", status: "flagged",  cardId: "CARD-4491", deviceId: "DEV-88B2", merchant: "CryptoExchange",   location: "Unknown" },
  { transactionId: "TXN-931055", customerId: "CUS-70014", customerName: "Sneha Patel",    amount: 320.00,  currency: "USD", channel: "E-commerce", timestamp: "2024-06-09T12:15:00Z", riskScore: 0.68, riskLevel: "high",      status: "approved", cardId: "CARD-2210", deviceId: "DEV-91A2", merchant: "TravelGo",         location: "Bangkok, TH" },
  { transactionId: "TXN-931056", customerId: "CUS-98765", customerName: "Rohit Bansal",   amount: 95.00,   currency: "USD", channel: "UPI",        timestamp: "2024-06-08T09:48:00Z", riskScore: 0.35, riskLevel: "low",       status: "approved", cardId: "CARD-5540", deviceId: "DEV-72F1", merchant: "FoodExpress",      location: "Noida, IN" },
  { transactionId: "TXN-931057", customerId: "CUS-60233", customerName: "Arjun Verma",    amount: 740.00,  currency: "USD", channel: "E-commerce", timestamp: "2024-06-10T10:30:00Z", riskScore: 0.49, riskLevel: "moderate",  status: "approved", cardId: "CARD-3320", deviceId: "DEV-4D21", merchant: "FurnitureHub",     location: "Pune, IN" },
  { transactionId: "TXN-931058", customerId: "CUS-81200", customerName: "Karthik Rao",    amount: 260.00,  currency: "USD", channel: "POS",        timestamp: "2024-06-07T17:20:00Z", riskScore: 0.38, riskLevel: "low",       status: "approved", cardId: "CARD-1180", deviceId: "DEV-2F10", merchant: "SportsStore",      location: "Hyderabad, IN" },
  { transactionId: "TXN-931059", customerId: "CUS-92017", customerName: "Divya Menon",    amount: 180.00,  currency: "USD", channel: "E-commerce", timestamp: "2024-06-09T08:44:00Z", riskScore: 0.44, riskLevel: "moderate",  status: "approved", cardId: "CARD-7702", deviceId: "DEV-6B33", merchant: "BeautyBox",        location: "Kochi, IN" },
];

export const mockCards: Card[] = [
  { cardId: "CARD-8831", customerId: "CUS-10482", last4: "4421", network: "Visa",       type: "credit", status: "active" },
  { cardId: "CARD-7712", customerId: "CUS-20391", last4: "8890", network: "Mastercard", type: "debit",  status: "active" },
  { cardId: "CARD-6611", customerId: "CUS-34821", last4: "1123", network: "Visa",       type: "credit", status: "active" },
  { cardId: "CARD-4491", customerId: "CUS-50911", last4: "7788", network: "RuPay",      type: "debit",  status: "frozen" },
  { cardId: "CARD-2210", customerId: "CUS-70014", last4: "3344", network: "Visa",       type: "credit", status: "active" },
  { cardId: "CARD-5520", customerId: "CUS-41120", last4: "9021", network: "Mastercard", type: "credit", status: "active" },
  { cardId: "CARD-3320", customerId: "CUS-60233", last4: "5567", network: "Visa",       type: "debit",  status: "active" },
  { cardId: "CARD-1180", customerId: "CUS-81200", last4: "2210", network: "RuPay",      type: "credit", status: "active" },
  { cardId: "CARD-7702", customerId: "CUS-92017", last4: "6612", network: "Visa",       type: "credit", status: "active" },
  { cardId: "CARD-5540", customerId: "CUS-98765", last4: "8899", network: "Mastercard", type: "debit",  status: "active" },
];

export const mockDevices: Device[] = [
  { deviceId: "DEV-91A2", fingerprint: "fp_9a2e11c4", os: "Android 13", firstSeen: "2024-05-20T10:00:00Z", lastSeen: "2024-06-11T09:12:00Z", linkedCustomers: 3 },
  { deviceId: "DEV-72F1", fingerprint: "fp_72f1bb09", os: "iOS 17",     firstSeen: "2024-04-15T08:00:00Z", lastSeen: "2024-06-11T07:40:00Z", linkedCustomers: 2 },
  { deviceId: "DEV-88B2", fingerprint: "fp_88b2ee71", os: "Android 12", firstSeen: "2024-06-01T18:00:00Z", lastSeen: "2024-06-11T07:20:00Z", linkedCustomers: 4 },
  { deviceId: "DEV-3C91", fingerprint: "fp_3c9100a1", os: "iOS 16",     firstSeen: "2023-11-01T12:00:00Z", lastSeen: "2024-06-10T21:30:00Z", linkedCustomers: 1 },
  { deviceId: "DEV-4D21", fingerprint: "fp_4d2155c9", os: "Android 14", firstSeen: "2023-08-12T09:00:00Z", lastSeen: "2024-06-09T14:00:00Z", linkedCustomers: 1 },
  { deviceId: "DEV-1A44", fingerprint: "fp_1a44aa10", os: "iOS 15",     firstSeen: "2022-03-04T10:00:00Z", lastSeen: "2024-06-10T18:12:00Z", linkedCustomers: 1 },
  { deviceId: "DEV-2F10", fingerprint: "fp_2f10cc33", os: "Android 13", firstSeen: "2023-02-11T10:00:00Z", lastSeen: "2024-06-08T11:30:00Z", linkedCustomers: 1 },
  { deviceId: "DEV-6B33", fingerprint: "fp_6b33dd44", os: "iOS 17",     firstSeen: "2023-06-09T10:00:00Z", lastSeen: "2024-06-10T15:50:00Z", linkedCustomers: 1 },
];

export const mockIdentities: Identity[] = [
  { identityId: "IDN-001", customerId: "CUS-10482", signal: "email_domain_age", value: "3 days",     confidence: "high"   },
  { identityId: "IDN-002", customerId: "CUS-10482", signal: "phone_reuse",      value: "5 accounts", confidence: "high"   },
  { identityId: "IDN-003", customerId: "CUS-20391", signal: "address_mismatch", value: "2 cities",   confidence: "medium" },
  { identityId: "IDN-004", customerId: "CUS-50911", signal: "email_domain_age", value: "1 day",      confidence: "high"   },
  { identityId: "IDN-005", customerId: "CUS-70014", signal: "phone_reuse",      value: "8 accounts", confidence: "high"   },
  { identityId: "IDN-006", customerId: "CUS-98765", signal: "ssn_mismatch",     value: "1 record",   confidence: "medium" },
];