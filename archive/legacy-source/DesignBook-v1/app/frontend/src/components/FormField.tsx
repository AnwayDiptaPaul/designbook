import type { UseFormRegister, FieldErrors } from "react-hook-form"
import { Label } from "./ui/label"
import { Input } from "./ui/input"

interface FormFieldProps {
  label: string
  name: string
  register: UseFormRegister<any>
  errors: FieldErrors<any>
  type?: string
  placeholder?: string
  min?: number
  max?: number
  step?: string | number
}

// A simple utility to get nested error messages safely
const getErrorMessage = (errors: any, path: string): string | undefined => {
  const parts = path.split('.')
  let current = errors
  for (const part of parts) {
    if (!current) return undefined
    current = current[part]
  }
  return current?.message as string | undefined
}

export function FormField({ 
  label, 
  name, 
  register, 
  errors, 
  type = "text", 
  placeholder,
  ...props
}: FormFieldProps) {
  const errorMessage = getErrorMessage(errors, name)

  return (
    <div className="space-y-2">
      <Label htmlFor={name} className={errorMessage ? "text-destructive" : ""}>
        {label}
      </Label>
      <Input
        id={name}
        type={type}
        placeholder={placeholder}
        {...register(name, { valueAsNumber: type === "number" })}
        className={errorMessage ? "border-destructive focus-visible:ring-destructive" : ""}
        {...props}
      />
      {errorMessage && (
        <p className="text-sm font-medium text-destructive">{errorMessage}</p>
      )}
    </div>
  )
}
