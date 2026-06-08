import { TicketDetailClient } from "@/app/dashboard/tickets/[ticketId]/ticket-detail-client";

export default async function TicketDetailPage({
  params,
}: {
  params: Promise<{ ticketId: string }>;
}) {
  const { ticketId } = await params;
  return <TicketDetailClient ticketId={ticketId} />;
}
