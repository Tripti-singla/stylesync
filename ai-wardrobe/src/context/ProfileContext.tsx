import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface UserProfile {
  name: string;
  email: string;
  phone: string;
  address: string;
  avatar: string;
}

const defaultProfile: UserProfile = {
  name: "",
  email: "",
  phone: "",
  address: "",
  avatar: "",
};

interface ProfileContextType {
  profile: UserProfile;
  updateProfile: (data: Partial<UserProfile>) => void;
  isProfileComplete: boolean;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<UserProfile>(() => {
    const saved = localStorage.getItem("profile");
    return saved ? JSON.parse(saved) : defaultProfile;
  });

  useEffect(() => {
    localStorage.setItem("profile", JSON.stringify(profile));
  }, [profile]);

  const updateProfile = (data: Partial<UserProfile>) => {
    setProfile((prev) => ({ ...prev, ...data }));
  };

  const isProfileComplete = !!(profile.name && profile.email);

  return (
    <ProfileContext.Provider value={{ profile, updateProfile, isProfileComplete }}>
      {children}
    </ProfileContext.Provider>
  );
}

export function useProfile() {
  const ctx = useContext(ProfileContext);
  if (!ctx) throw new Error("useProfile must be used within ProfileProvider");
  return ctx;
}
