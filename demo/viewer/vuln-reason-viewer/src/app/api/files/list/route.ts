import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(request: NextRequest) {
  try {
    const dataDir = path.join(process.cwd(), 'data');
    
    // Check if directory exists
    if (!fs.existsSync(dataDir)) {
      return NextResponse.json(
        { error: 'Data directory does not exist' },
        { status: 404 }
      );
    }

    // Read directory contents
    const files = fs.readdirSync(dataDir);
    
    // Get file stats for more information
    const fileDetails = files.map(file => {
      const filePath = path.join(dataDir, file);
      const stats = fs.statSync(filePath);
      return {
        name: file,
        path: `/data/${file}`,
        size: stats.size,
        isDirectory: stats.isDirectory(),
        createdAt: stats.birthtime,
        modifiedAt: stats.mtime
      };
    });

    return NextResponse.json({ files: fileDetails });
  } catch (error) {
    console.error('Error listing files:', error);
    return NextResponse.json(
      { error: 'Failed to list files' },
      { status: 500 }
    );
  }
}