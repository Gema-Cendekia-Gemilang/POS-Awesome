// Language helper for POS Awesome
export function initLanguage() {
  // Get saved language preference or use system default
  const savedLang = localStorage.getItem('posawesome_language');
  
  if (savedLang && savedLang !== frappe.boot.lang) {
    // Set Frappe language if different from saved preference
    frappe.boot.lang = savedLang;
  }
}

export function getCurrentLanguage() {
  return localStorage.getItem('posawesome_language') || frappe.boot.lang || 'en';
}

export function setLanguage(lang) {
  localStorage.setItem('posawesome_language', lang);
  frappe.boot.lang = lang;
}
