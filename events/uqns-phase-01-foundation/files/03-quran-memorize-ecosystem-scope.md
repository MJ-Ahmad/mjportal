# Quran Memorize Ecosystem — Initial Scope

## README-তে উল্লেখিত components

- Student Portal
- Teacher Portal
- Supervisor Dashboard
- Principal Dashboard
- Analytics Engine
- Reporting System
- Attendance System
- Academic Tracking
- Governance Framework

## এই ইভেন্টে নির্ধারণ করতে হবে

- এই ecosystem UQNS repository-র কোন অংশে থাকবে
- এটি `apps/`, `profiles/`, `analytics/`, `api/` ও `governance/`-এর সাথে কীভাবে যুক্ত হবে
- student, teacher, supervisor ও principal role-এর প্রাথমিক responsibility
- ব্যক্তিগত শিক্ষার্থী তথ্য কীভাবে গোপন ও access-controlled থাকবে
- attendance, analytics ও reporting-এর জন্য কোন data governance দরকার
- Quran content/navigation platform-এর সাথে integration boundary কী হবে

## প্রাথমিক mapping — অনুমোদনের অপেক্ষায়

- `apps/` — সংশ্লিষ্ট portal ও dashboard app boundary
- `profiles/` — students, teachers, admins ও guests-এর profile model
- `analytics/` — progress, habits, completion ও reporting-related modules
- `api/` — অনুমোদিত data exchange boundary
- `governance/` — privacy, access, ethics, retention ও stewardship policy
- `documentation/` — onboarding, architecture ও operating procedures

Student data ও access policy review না করে বাস্তব ব্যক্তিগত তথ্য repository-তে
রাখা যাবে না। Mapping final approval-এর আগে draft হিসেবেই বিবেচ্য।
