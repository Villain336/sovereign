'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckoutStep } from '@/types';
import CheckoutSteps from '@/components/checkout/CheckoutSteps';
import OrderSummary from '@/components/checkout/OrderSummary';
import Button from '@/components/ui/Button';
import SnowGlobeLoader from '@/components/three/SnowGlobeLoader';
import SceneLoader from '@/components/three/SceneLoader';
import Link from 'next/link';

export default function CheckoutPage() {
  const [step, setStep] = useState<CheckoutStep>('information');

  const nextStep = () => {
    if (step === 'information') setStep('shipping');
    else if (step === 'shipping') setStep('payment');
    else if (step === 'payment') setStep('confirmation');
  };

  const prevStep = () => {
    if (step === 'shipping') setStep('information');
    else if (step === 'payment') setStep('shipping');
  };

  return (
    <div className="relative min-h-screen pt-28 pb-20">
      {/* Snow Globe Background — ALL shapes floating */}
      <div className="fixed inset-0 z-0 opacity-40">
        <SnowGlobeLoader />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 md:px-16">
        {/* Steps indicator */}
        <div className="mb-10">
          <CheckoutSteps current={step} />
        </div>

        <AnimatePresence mode="wait">
          {step === 'confirmation' ? (
            <motion.div
              key="confirmation"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-20"
            >
              <div className="w-48 h-48 mx-auto mb-8">
                <SceneLoader variant="minimal" />
              </div>
              <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-graphite">ORDER</span>
              <h1 className="font-display text-5xl md:text-7xl font-light tracking-tight mt-2">CONFIRMED</h1>
              <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.2em] mt-6 max-w-md mx-auto leading-relaxed">
                ORDER #SV-{Math.random().toString(36).substring(2, 8).toUpperCase()}
                <br /><br />
                YOUR GARMENTS ARE BEING PREPARED WITH PRECISION.
                YOU WILL RECEIVE A CONFIRMATION EMAIL SHORTLY.
              </p>
              <div className="mt-10">
                <Link href="/collections">
                  <Button variant="filled" size="lg">CONTINUE SHOPPING</Button>
                </Link>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Form */}
                <div className="lg:col-span-2">
                  <div className="bg-sovereign-white/90 backdrop-blur-md p-8 border border-sovereign-silver">
                    {step === 'information' && (
                      <div>
                        <h2 className="font-mono text-xs tracking-[0.3em] mb-8">INFORMATION</h2>
                        <div className="flex flex-col gap-5">
                          <input type="email" placeholder="EMAIL" className="w-full bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                          <div className="grid grid-cols-2 gap-4">
                            <input type="text" placeholder="FIRST NAME" className="bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                            <input type="text" placeholder="LAST NAME" className="bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                          </div>
                          <input type="text" placeholder="ADDRESS" className="w-full bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                          <div className="grid grid-cols-3 gap-4">
                            <input type="text" placeholder="CITY" className="bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                            <input type="text" placeholder="STATE" className="bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                            <input type="text" placeholder="ZIP" className="bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                          </div>
                        </div>
                      </div>
                    )}

                    {step === 'shipping' && (
                      <div>
                        <h2 className="font-mono text-xs tracking-[0.3em] mb-8">SHIPPING METHOD</h2>
                        <div className="flex flex-col gap-3">
                          {[
                            { label: 'STANDARD', desc: '5-7 BUSINESS DAYS', price: 'FREE OVER $100' },
                            { label: 'EXPRESS', desc: '2-3 BUSINESS DAYS', price: '$12' },
                          ].map((method) => (
                            <label key={method.label} className="flex items-center justify-between p-4 border border-sovereign-silver hover:border-sovereign-carbon transition-colors cursor-pointer">
                              <div className="flex items-center gap-3">
                                <input type="radio" name="shipping" defaultChecked={method.label === 'STANDARD'} className="accent-sovereign-carbon" />
                                <div>
                                  <span className="font-mono text-xs tracking-[0.2em]">{method.label}</span>
                                  <span className="font-mono text-[9px] text-sovereign-graphite tracking-[0.15em] block mt-1">{method.desc}</span>
                                </div>
                              </div>
                              <span className="font-mono text-xs tracking-[0.15em]">{method.price}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}

                    {step === 'payment' && (
                      <div>
                        <h2 className="font-mono text-xs tracking-[0.3em] mb-8">PAYMENT</h2>
                        <div className="flex flex-col gap-5">
                          <input type="text" placeholder="CARD NUMBER" className="w-full bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                          <div className="grid grid-cols-2 gap-4">
                            <input type="text" placeholder="MM / YY" className="bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                            <input type="text" placeholder="CVC" className="bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                          </div>
                          <div className="mt-4">
                            <span className="font-mono text-[10px] tracking-[0.2em] text-sovereign-graphite">PROMO CODE</span>
                            <div className="flex gap-3 mt-2">
                              <input type="text" placeholder="ENTER CODE" className="flex-1 bg-transparent border-b border-sovereign-silver pb-3 font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none focus:border-sovereign-carbon transition-colors" />
                              <Button variant="outline" size="sm">APPLY</Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Navigation buttons */}
                    <div className="flex justify-between mt-10">
                      {step !== 'information' ? (
                        <Button variant="ghost" onClick={prevStep}>BACK</Button>
                      ) : (
                        <div />
                      )}
                      <Button variant="filled" size="lg" onClick={nextStep}>
                        {step === 'payment' ? 'PLACE ORDER' : 'CONTINUE'}
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Order Summary */}
                <div className="lg:col-span-1">
                  <OrderSummary />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
