// Oddiy o'zbek tarjimalari (keyin rus tili qo'shilishi mumkin)
export const uz = {
  appName: "Nazartepa 103",
  tagline: "AI asosidagi tez tibbiy yordam dispetcherligi",
  login: "Kirish",
  logout: "Chiqish",
  email: "Email",
  password: "Parol",
  signIn: "Tizimga kirish",
  loginError: "Email yoki parol noto'g'ri",
  dashboard: "Boshqaruv paneli",
  calls: "Murojaatlar",
  ambulances: "Brigadalar",
  map: "Xarita",
  liveMap: "Jonli xarita",
  noCalls: "Murojaatlar yo'q",
  complaint: "Shikoyat",
  status: "Holat",
  priority: "Ustuvorlik",
  brigade: "Brigada",
  recommendedBrigade: "Tavsiya etilgan brigada",
  confidence: "Ishonchlilik",
  aiTriage: "AI triaj",
  phone: "Telefon",
  address: "Manzil",
  dispatch: "Tayinlash",
  triage: "Triaj",
  markTriaged: "Triaj qilingan deb belgilash",
  connected: "Ulangan",
  disconnected: "Uzilgan",
  eta: "ETA",
  distance: "Masofa",
  minutes: "daq",
  km: "km",
  refresh: "Yangilash",
  filterAll: "Barchasi",
} as const;

export const priorityLabel: Record<string, string> = {
  red: "Qizil (shoshilinch)",
  yellow: "Sariq",
  green: "Yashil",
};

export const statusLabel: Record<string, string> = {
  new: "Yangi",
  triaged: "Triaj qilingan",
  dispatched: "Tayinlangan",
  en_route: "Yo'lda",
  on_scene: "Joyida",
  completed: "Yakunlangan",
  cancelled: "Bekor qilingan",
};

export const ambulanceStatusLabel: Record<string, string> = {
  available: "Bo'sh",
  dispatched: "Tayinlangan",
  en_route: "Yo'lda",
  on_scene: "Joyida",
  busy: "Band",
  offline: "Oflayn",
};
