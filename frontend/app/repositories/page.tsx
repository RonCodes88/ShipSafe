import { ProjectGrid } from '@/components/ProjectGrid'
import { Suspense } from 'react'

export default function RepositoriesPage() {
  return (
    <div className="p-6">
      <Suspense fallback={<div className="flex items-center justify-center py-12"><div className="w-8 h-8 border-4 border-gray-200 border-t-black rounded-full animate-spin"></div></div>}>
        <ProjectGrid />
      </Suspense>
    </div>
  )
}

