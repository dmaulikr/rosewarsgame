//
//  Attribute.m
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 12/27/12.
//
//

#import "RangeAttribute.h"

@interface RangeAttribute()

- (AttributeRange)calculateFinalRange:(AttributeRange)finalRange fromBonus:(NSUInteger)bonus;

@end

@implementation RangeAttribute

@synthesize finalRange = _finalRange;
@synthesize delegate = _delegate;
@synthesize valueAffectedByBonuses = _valueAffectedByBonuses;
@synthesize valueLimit = _valueLimit;

- (id)initWithStartingRange:(AttributeRange)startingRange {
    
    self = [super initWithRange:startingRange];
    
    if (self) {
        
        _rawBonuses = [[NSMutableArray alloc] init];
        _timedBonuses = [[NSMutableArray alloc] init];
        
        _valueAffectedByBonuses = kRangedAttributeLowerValue;
        
        _finalRange = self.baseRange;
    }
    
    return self;
}

- (TimedBonus*)addTimedBonus:(TimedBonus *)timedBonus {
    
    [_timedBonuses addObject:timedBonus];
    
    [timedBonus startTimedBonus:self];
    
    if ([_delegate respondsToSelector:@selector(rangeAttribute:addedTimedBonus:)]) {
        [_delegate rangeAttribute:self addedTimedBonus:timedBonus];
    }
    
    return timedBonus;
}

- (RawBonus*)addRawBonus:(RawBonus *)rawBonus {
    
    [_rawBonuses addObject:rawBonus];
    
    if ([_delegate respondsToSelector:@selector(rangeAttribute:addedRawBonus:)]) {
        [_delegate rangeAttribute:self addedRawBonus:rawBonus];
    }
    
    return rawBonus;
}

- (NSUInteger)getRawBonusValue {
    
    // Add values from raw bonuses
    NSUInteger rawBonusValue = 0;
    
    for (RawBonus *rawbonus in _rawBonuses) {
        
        rawBonusValue += rawbonus.bonusValue;
    }
    
    return rawBonusValue;
}

- (NSUInteger)getTimedBonusValue {
    
    // Add values from final bonuses
    NSUInteger timedBonusValue = 0;
    
    for (TimedBonus *timedbonus in _timedBonuses) {
        
        timedBonusValue += timedbonus.bonusValue;
    }
    
    return timedBonusValue;
}

- (void)removeTimedBonus:(TimedBonus *)timedBonus {
    
    if ([_timedBonuses containsObject:timedBonus]) {
        [_timedBonuses removeObject:timedBonus];
        
        if ([_delegate respondsToSelector:@selector(rangeAttribute:removedTimedBonus:)]) {
            [_delegate rangeAttribute:self removedTimedBonus:timedBonus];
        }
    }
}

- (void)removeRawBonus:(RawBonus *)rawBonus {
    
    if ([_rawBonuses containsObject:rawBonus]) {
        [_rawBonuses removeObject:rawBonus];
        
        if ([_delegate respondsToSelector:@selector(rangeAttribute:removedRawBonus:)]) {
            [_delegate rangeAttribute:self removedRawBonus:rawBonus];
        }
    }
}

- (AttributeRange)calculateFinalRange:(AttributeRange)finalRange fromBonus:(NSUInteger)bonus {
    
    AttributeRange calculatedFinalRange;
    
    if (_valueAffectedByBonuses == kRangedAttributeLowerValue) {
        
        NSUInteger lowerValue = finalRange.lowerValue - bonus;
        
        if (_valueLimit != 0) {
            lowerValue = MAX(_valueLimit, lowerValue);
        }

        calculatedFinalRange = MakeAttributeRange(lowerValue, finalRange.upperValue);
    }
    else if (_valueAffectedByBonuses == kRangedAttributeUpperValue) {
        
        NSUInteger upperValue = finalRange.upperValue + bonus;
        
        if (_valueLimit != 0) {
            upperValue = MIN(_valueLimit, upperValue);
        }
        
        calculatedFinalRange = MakeAttributeRange(finalRange.lowerValue, upperValue);
    }
    
    return calculatedFinalRange;
}

- (AttributeRange)calculateValue {
    
    _finalRange = self.baseRange;
    
    NSUInteger rawBonusValue = [self getRawBonusValue];
    
    _finalRange = [self calculateFinalRange:_finalRange fromBonus:rawBonusValue];

    NSUInteger timedBonusValue = [self getTimedBonusValue];
    
    _finalRange = [self calculateFinalRange:_finalRange fromBonus:timedBonusValue];
        
    return _finalRange;
}

- (NSUInteger)getTotalBonusValue {
    
    return [self getRawBonusValue] + [self getTimedBonusValue];
}

- (AttributeRange)finalValue {

    return [self calculateValue];
}

@end
