import { Suspense } from "react";
import LibraryContent from "./LibraryContent";

export default function LibraryPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-gray-400">Loading threat library...</div>}>
      <LibraryContent />
    </Suspense>
  );
}
