"use client";

import * as React from "react";
import { Search, ChevronLeft, ChevronRight, Inbox } from "lucide-react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/ui/table";
import { Input } from "@/shared/ui/input";
import { Button } from "@/shared/ui/button";
import { useDebounce } from "@/core/hooks/use-debounce";

export interface ColumnDef<TData> {
  header: string | React.ReactNode;
  accessorKey?: keyof TData;
  cell?: (item: TData) => React.ReactNode;
  className?: string;
}

interface BaseDataTableProps<TData> {
  columns: ColumnDef<TData>[];
  data: TData[];
  searchPlaceholder?: string;
  pageSize?: number;
  emptyMessage?: string;
  paginationText?: (start: number, end: number, total: number) => string;
}

interface ClientDataTableProps<TData> extends BaseDataTableProps<TData> {
  mode?: "client";
  searchKey?: keyof TData;
}

interface ServerDataTableProps<TData> extends BaseDataTableProps<TData> {
  mode: "server";
  pageCount: number;
  rowCount: number;
  pageIndex: number;
  onPageChange: (page: number) => void;
  onSearchChange?: (query: string) => void;
}

type DataTableProps<TData> =
  | ClientDataTableProps<TData>
  | ServerDataTableProps<TData>;

export function DataTable<TData>(props: DataTableProps<TData>) {
  const {
    data,
    columns,
    searchPlaceholder = "Search...",
    pageSize = 5,
    emptyMessage = "No results found.",
    paginationText,
    mode = "client",
  } = props;

  const isServer = mode === "server";

  const [localSearchQuery, setLocalSearchQuery] = React.useState("");
  const debouncedSearchQuery = useDebounce(localSearchQuery, 300);
  const [clientCurrentPage, setClientCurrentPage] = React.useState(1);

  React.useEffect(() => {
    if (isServer && "onSearchChange" in props && props.onSearchChange) {
      props.onSearchChange(debouncedSearchQuery);
    }
  }, [debouncedSearchQuery, isServer, props]);

  const processedData = React.useMemo(() => {
    if (isServer) return data;

    const clientProps = props as ClientDataTableProps<TData>;
    let filtered = data;

    if (clientProps.searchKey && localSearchQuery) {
      filtered = data.filter((item) => {
        const value = item[clientProps.searchKey!];
        if (typeof value === "string") {
          return value.toLowerCase().includes(localSearchQuery.toLowerCase());
        }
        return false;
      });
    }

    const startIndex = (clientCurrentPage - 1) * pageSize;
    return filtered.slice(startIndex, startIndex + pageSize);
  }, [data, isServer, props, localSearchQuery, clientCurrentPage, pageSize]);

  const currentPage = isServer
    ? (props as ServerDataTableProps<TData>).pageIndex
    : clientCurrentPage;

  const totalPages = isServer
    ? (props as ServerDataTableProps<TData>).pageCount
    : Math.max(
        1,
        Math.ceil(
          (props as ClientDataTableProps<TData>).searchKey && localSearchQuery
            ? processedData.length
            : data.length / pageSize,
        ),
      );

  const totalEntries = isServer
    ? (props as ServerDataTableProps<TData>).rowCount
    : data.length;
  const currentStart =
    totalEntries === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const currentEnd = isServer
    ? Math.min(currentPage * pageSize, totalEntries)
    : Math.min(currentStart + processedData.length - 1, totalEntries);

  const handlePageChange = (newPage: number) => {
    if (isServer && "onPageChange" in props) {
      props.onPageChange(newPage);
    } else {
      setClientCurrentPage(newPage);
    }
  };

  React.useEffect(() => {
    if (!isServer) setClientCurrentPage(1);
  }, [localSearchQuery, isServer]);

  const showSearch = isServer
    ? "onSearchChange" in props
    : "searchKey" in props;

  const containerHeight = `calc(48px + (${pageSize} * 64px) + 2px)`;

  return (
    <div className="w-full space-y-4">
      {/* TOOLBAR */}
      {showSearch && (
        <div className="flex items-center justify-end">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder={searchPlaceholder}
              value={localSearchQuery}
              onChange={(e) => setLocalSearchQuery(e.target.value)}
              className="pl-9 bg-background/50 focus-visible:ring-1 focus-visible:ring-primary/50 transition-all"
            />
          </div>
        </div>
      )}

      <div
        className="rounded-xl border border-border/60 bg-card/40 backdrop-blur-sm shadow-sm flex flex-col overflow-hidden relative [&>div]:overflow-hidden"
        style={{ height: containerHeight }}
      >
        <Table className="flex-1 w-full">
          <TableHeader className="bg-muted/40 border-b border-border/60 sticky top-0 z-10">
            <TableRow className="hover:bg-transparent h-12">
              {columns.map((col, index) => (
                <TableHead
                  key={index}
                  className={`font-medium ${col.className || ""}`}
                >
                  {col.header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody className="align-top">
            {processedData.length === 0 ? (
              <TableRow className="hover:bg-transparent border-0">
                <TableCell
                  colSpan={columns.length}
                  className="h-full text-center text-muted-foreground align-middle"
                >
                  <div className="flex flex-col items-center justify-center space-y-2 mt-12">
                    <Inbox className="h-8 w-8 text-muted-foreground/30" />
                    <p>{emptyMessage}</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              processedData.map((item, rowIndex) => (
                <TableRow
                  key={rowIndex}
                  className="hover:bg-muted/40 transition-colors border-b-border/40 last:border-b h-16"
                >
                  {columns.map((col, colIndex) => (
                    <TableCell
                      key={colIndex}
                      className={`py-2 ${col.className || ""}`}
                    >
                      {col.cell
                        ? col.cell(item)
                        : col.accessorKey
                          ? String(item[col.accessorKey] ?? "")
                          : null}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between px-1">
        <div className="text-sm text-muted-foreground font-medium">
          {paginationText
            ? paginationText(currentStart, currentEnd, totalEntries)
            : `Showing ${currentStart} to ${currentEnd} of ${totalEntries} entries`}
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8 rounded-lg border-border/60 shadow-sm"
            onClick={() => handlePageChange(Math.max(currentPage - 1, 1))}
            disabled={currentPage === 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div className="text-sm font-medium w-12 text-center text-foreground tabular-nums">
            {currentPage} / {totalPages}
          </div>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8 rounded-lg border-border/60 shadow-sm"
            onClick={() =>
              handlePageChange(Math.min(currentPage + 1, totalPages))
            }
            disabled={currentPage === totalPages}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
