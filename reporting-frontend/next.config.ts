import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  turbopack: {
    root: path.join(__dirname, '..'), // Set your project root directory
  },
  // Add other config options as needed
};

export default nextConfig;