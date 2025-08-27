import Link from 'next/link';

export default function Home() {
  return (
    <div className="container mx-auto p-8 flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Vulnerability Results Editor</h1>
      <p className="text-lg mb-8">Analyze and explore vulnerability detection results</p>
      <Link href="/editor" 
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
        Go to Editor
      </Link>
      <Link href="/file-manager"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
        File Manager
      </Link>
    </div>
  );
}